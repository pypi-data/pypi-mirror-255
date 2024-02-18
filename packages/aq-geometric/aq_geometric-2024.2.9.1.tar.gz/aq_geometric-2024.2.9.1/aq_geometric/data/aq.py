import time
from datetime import datetime, timedelta
from typing import List, Union, Callable, Tuple, Dict

import h3
import torch
import numpy as np
import pandas as pd
from torch_geometric.data import Data
from sqlalchemy.sql import text
from aq_utilities.engine.psql import get_engine


def load_hourly_data(
    engine: "sqlalchemy.engine.base.Engine",
    table_name: str = "hourly_data",
    features: List[str] = ["PM2.5"],
    start_date: str = "2020-01-01",
    end_date: str = "2024-01-01",
    aqsid: Union[List[str], None] = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """Load the dataframe from the database."""
    measurements = ",".join(f"'{m}'" for m in features)
    aqsid = ",".join(f"'{a}'" for a in aqsid) if aqsid is not None else None
    aqsid_override = f"AND d.aqsid IN ({aqsid})" if aqsid is not None else ""
    query = f"SELECT d.aqsid, d.timestamp, d.measurement, d.value FROM {table_name} AS d WHERE d.timestamp >= '{start_date}' AND d.timestamp < '{end_date}' AND d.measurement IN ({measurements}) {aqsid_override} GROUP BY d.aqsid, d.timestamp, d.measurement, d.value ORDER BY d.timestamp;"

    if verbose: print(f"[{datetime.now()}] executing query: {query}")

    # execute the query
    with engine.connect() as conn:
        query_start = time.time()
        df = pd.read_sql_query(text(query), conn)
        query_end = time.time()
        if verbose:
            print(
                f"[{datetime.now()}] query executed in {query_end - query_start:.2f} seconds"
            )

    if verbose: print(f"[{datetime.now()}] dataframe shape: {df.shape}")

    return df


def load_hourly_data_from_fp(
    fp: str = "data.csv",
    verbose: bool = False,
) -> pd.DataFrame:
    """Load the dataframe from the database."""
    df = pd.read_csv(fp)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["aqsid"] = df["aqsid"].astype(str)

    if verbose: print(f"[{datetime.now()}] dataframe shape: {df.shape}")

    return df


def load_stations_info(
    engine: "sqlalchemy.engine.base.Engine",
    table_name: str = "stations_info",
    query_date: str = "2022-01-01",
    aqsid: Union[List[str], None] = None,
    verbose: bool = False,
) -> pd.DataFrame:
    # get the station information for these stations from the database
    aqsid = ",".join(f"'{s}'" for s in aqsid) if aqsid is not None else None
    aqsid_override = f"AND d.aqsid IN ({aqsid})" if aqsid is not None else ""
    query = f"SELECT d.aqsid, d.latitude, d.longitude, d.elevation FROM {table_name} AS d WHERE d.timestamp = '{query_date}' {aqsid_override} ORDER BY d.aqsid;"

    if verbose: print(f"[{datetime.now()}] executing query: {query}")

    with engine.connect() as conn:
        query_start = time.time()
        df_stations = pd.read_sql_query(text(query), conn)
        query_end = time.time()
        if verbose:
            print(
                f"[{datetime.now()}] query executed in {query_end - query_start:.2f} seconds"
            )

    if verbose:
        print(f"[{datetime.now()}] dataframe shape: {df_stations.shape}")

    return df_stations


def load_stations_info_from_fp(
    fp: str = "stations_info.csv",
    verbose: bool = False,
) -> pd.DataFrame:
    """Load the dataframe from the database."""
    df = pd.read_csv(fp)
    df["aqsid"] = df["aqsid"].astype(str)

    if verbose: print(f"[{datetime.now()}] dataframe shape: {df.shape}")

    return df


def process_df(
    df: pd.DataFrame,
    stations_info: pd.DataFrame,
    start_time: str = "2020-01-01",
    end_time: str = "2024-01-01",
    time_step: str = "1H",
    aggregation_method: Union[Callable, str] = "mean",
    nan_value: Union[float, int] = -1,
    verbose: bool = False,
) -> pd.DataFrame:
    """Take the raw DataFrame from the database and process it into a fixed-station, fixed-index format."""
    # make a datetime index for the full range
    date_range = pd.date_range(start=start_time, end=end_time, freq=time_step)

    if verbose: print(f"[{datetime.now()}] processing dataframe")

    # we would like df to be indexed on time and have columns for each station
    df = df[["aqsid", "timestamp",
             "value"]].groupby(["timestamp", "aqsid"]).aggregate({
                 "value":
                 aggregation_method
             }).reset_index().pivot(index="timestamp", columns="aqsid",
                                    values="value").reindex(date_range)
    # undo the pivot so that we have a column for timestamp, a column for aqsid, and a column for value
    df = df.unstack().reset_index().rename(columns={
        "level_1": "timestamp",
        0: "value"
    })
    # join the lat, lon, elevation information to the main dataframe
    stations_info = stations_info.groupby("aqsid").first()
    df = df.join(stations_info, on="aqsid", how="inner")

    if verbose: print(f"[{datetime.now()}] dataframe shape: {df.shape}")

    # fill missing values with negative 1
    df = df.fillna(nan_value)

    return df


def determine_leaf_resolution(
    df: pd.DataFrame,
    min_h3_resolution: int = 0,
    max_h3_resolution: int = 12,
    verbose: bool = False,
) -> int:
    """Determine the leaf resolution that will give us unique hexagons for each station."""
    # we have one station that is at the exact same location as another station, so we need to drop one of them
    assert "latitude" in df.columns and "longitude" in df.columns, "df must have latitude and longitude columns"
    assert "aqsid" in df.columns, "df must have aqsid column"

    df = df.groupby(["latitude", "longitude"]).aggregate({
        "aqsid": "first"
    }).reset_index()

    # find the MAX_H3_RESOLUTION that will give us unique hexagons for each station
    leaf_h3_resolution: int = min_h3_resolution
    if verbose: print(f"[{datetime.now()}] determining leaf resolution")
    for i in range(min_h3_resolution, max_h3_resolution):
        if verbose: print(f"[{datetime.now()}] trying resolution {i}")
        if len(df["aqsid"].values) == len(
                df.apply(lambda x: h3.geo_to_h3(x.latitude, x.longitude, i),
                         axis=1).unique()):
            leaf_h3_resolution = i
            if verbose: print(f"[{datetime.now()}] found resolution {i}")
            break

    return leaf_h3_resolution


def process_edges(
    df: pd.DataFrame,
    min_h3_resolution: int,
    leaf_h3_resolution: int,
    make_undirected: bool,
    with_edge_features: bool,
    min_to_root_edge_distance: float = 0.0,
    include_root_node: bool = True,
    verbose: bool = False,
) -> Union[List[Tuple[int, int]], List[Tuple[int, int, float]], List[Tuple[
        int, int]]]:
    """Process the edges and edge features for the graph."""
    assert "latitude" in df.columns and "longitude" in df.columns, "df must have latitude and longitude columns"

    # we have one more more stations with the exact same location as another station, so we need to drop one of them
    df = df.groupby(["latitude", "longitude"]).aggregate({
        "aqsid": "first"
    }).reset_index()

    if verbose:
        print(f"[{datetime.now()}] processing resolution {leaf_h3_resolution}")
    # map the h3 index at the leaf resolution to the station
    df["h3_index"] = df.apply(
        lambda x: h3.geo_to_h3(x.latitude, x.longitude, leaf_h3_resolution),
        axis=1)

    edges = [
    ]  # tuples of (h3_index1, h3_index2), when concatenated will be shape (2, num_edges)
    edge_attr = [
    ]  # tuples of (h3_index1, h3_index2, distance), when concatenated will be shape (num_edges, 1)
    node_counter = 0  # counter for the node ids

    # iterate through the h3 indices between the leaf resolution and the coarsest resolution
    for next_h3_resolution in range(leaf_h3_resolution - 1,
                                    min_h3_resolution - 2, -1):
        # add edges for the current resolution
        node_counter += len(df["h3_index"].values)
        current_resolution_nodes = set(df["h3_index"].unique().tolist())
        for _, row in df.iterrows():
            # we already have all h3 indices at this resolution, but we need to see if any of them are neighbors
            # get the neighbors of the current h3 index
            neighbors = h3.k_ring(row.h3_index, 1)
            # check if any of the neighbors are in the current resolution. note that k_ring returns the current h3 index as well
            if any([
                    n in current_resolution_nodes for n in neighbors
                    if n != row.h3_index
            ]):
                # add the edges
                for n in neighbors:
                    if n in current_resolution_nodes:
                        edges.append((row.h3_index, n))
                        if make_undirected: edges.append((n, row.h3_index))
                        # we need to get lat-lon for the distance calculation
                        lat1, lon1 = h3.h3_to_geo(row.h3_index)
                        lat2, lon2 = h3.h3_to_geo(n)
                        if with_edge_features:
                            distance = h3.point_dist((lat1, lon1),
                                                     (lat2, lon2))
                            edge_attr.append((row.h3_index, n, distance))
                            if make_undirected:
                                edge_attr.append((n, row.h3_index, distance))

        if next_h3_resolution < min_h3_resolution: break
        if verbose:
            print(
                f"[{datetime.now()}] processing resolution {next_h3_resolution}"
            )
        # get the h3 index for each station at the next_resolution
        df["next_h3_index"] = df.apply(
            lambda x: h3.h3_to_parent(x.h3_index, next_h3_resolution), axis=1)
        # add edges for the next resolution
        edges.extend(df[["h3_index", "next_h3_index"
                         ]].apply(lambda x: (x.h3_index, x.next_h3_index),
                                  axis=1).values)
        if make_undirected:
            edges.extend(df[["h3_index", "next_h3_index"
                             ]].apply(lambda x: (x.next_h3_index, x.h3_index),
                                      axis=1).values)
        if with_edge_features:
            new_edge_attrs = [
                (v[0], v[1],
                 h3.point_dist(h3.h3_to_geo(v[0]), h3.h3_to_geo(v[1])))
                for v in df[["h3_index", "next_h3_index"]].to_numpy()
            ]
            edge_attr.extend(new_edge_attrs)
            if make_undirected:
                edge_attr.extend([(v[1], v[0], v[2]) for v in new_edge_attrs])
        # group by the next h3 index
        df = df.groupby("next_h3_index").aggregate({
            "aqsid": "first"
        }).reset_index()  # we don't need to aggregate the values
        # rename the h3 index to the current h3 index
        df = df.rename(columns={"next_h3_index": "h3_index"})

    # add another parent node for the entire graph if needed
    if include_root_node:
        if verbose: print(f"[{datetime.now()}] adding root node")
        root_node_id = "root"
        edges.extend([(root_node_id, n) for n in df["h3_index"].values])
        if with_edge_features:
            edge_attr.extend([(n, root_node_id, min_to_root_edge_distance)
                              for n in df["h3_index"].values
                              ])  # for now we have 0 for the distance

    if verbose: print(f"[{datetime.now()}] processed {len(edges)} edges")
    if with_edge_features:
        assert len(edges) == len(edge_attr)
        return edges, edge_attr
    else:
        return edges, edge_attr


def process_feature(
    df: pd.DataFrame,
    start_time: str,
    end_time: str,
    aggregation_method: Union[Callable, str],
    min_h3_resolution: int,
    leaf_h3_resolution: int,
    include_root_node: bool = True,
    verbose: bool = False,
) -> np.ndarray:
    """Process a single feature DataFrame to a set of node-level features."""
    # ensure that the columns exist
    assert "timestamp" in df.columns
    assert "latitude" in df.columns
    assert "longitude" in df.columns
    assert "aqsid" in df.columns
    assert "value" in df.columns

    # get the features from start time to end time
    df = df[(df.timestamp >= start_time)
            & (df.timestamp <= end_time)].copy(deep=True)
    df.reset_index(inplace=True)

    if verbose: print(f"[{datetime.now()}] processing feature")

    # we have one station that is at the exact same location as another station, so we need to drop one of them
    df = df.groupby(["timestamp", "latitude", "longitude"]).aggregate({
        "aqsid":
        "first",
        "value":
        aggregation_method
    }).reset_index()
    if verbose: print(f"[{datetime.now()}] dataframe shape: {df.shape}")

    # map the h3 index at the leaf resolution to the station
    # pivot the dataframe so that we have a column for each timestamp and a row for each h3 index
    df = df.pivot(index=["latitude", "longitude"], columns="timestamp",
                  values="value").reset_index()
    if verbose:
        print(f"[{datetime.now()}] pivoted dataframe shape: {df.shape}")

    if verbose:
        print(f"[{datetime.now()}] processing resolution {leaf_h3_resolution}")
    df["h3_index"] = df.apply(
        lambda x: h3.geo_to_h3(x.latitude, x.longitude, leaf_h3_resolution),
        axis=1)
    df.drop(columns=["latitude", "longitude"], inplace=True)

    node_features = [
    ]  # tuples of (h3_index, value_t1, ..., value_tn), when concatenated will be shape (num_nodes, num_timestamps)

    # iterate through the h3 indices between the leaf resolution and the coarsest resolution
    for next_h3_resolution in range(leaf_h3_resolution - 1,
                                    min_h3_resolution - 2, -1):
        # ensure that the h3_index is the first column
        col_names = df.columns.tolist()
        col_names.remove("h3_index")
        # sort the columns by timestamp
        col_names.sort()
        col_names.insert(0, "h3_index")
        df = df[col_names]
        # add values for the current resolution
        node_features.extend(df.to_numpy())

        if next_h3_resolution < min_h3_resolution: break
        if verbose:
            print(
                f"[{datetime.now()}] processing resolution {next_h3_resolution}"
            )
        # get the h3 index for each station at the next_resolution
        df["next_h3_index"] = df.apply(
            lambda x: h3.h3_to_parent(x.h3_index, next_h3_resolution), axis=1)
        # group by the next h3 index
        df.drop(columns=["h3_index"], inplace=True)
        df = df.groupby("next_h3_index").aggregate(
            aggregation_method).reset_index()
        # rename the h3 index to the current h3 index
        df = df.rename(columns={"next_h3_index": "h3_index"})

    # add another parent node for the entire graph
    if include_root_node:
        if verbose: print(f"[{datetime.now()}] adding root node")
        root_node_id = "root"
        df.drop(columns=["h3_index"], inplace=True)
        node_features.append(
            np.concatenate((np.array([root_node_id]),
                            df.apply(aggregation_method).values.T)))

    return node_features


def process_graph(
    features_df: Union[pd.DataFrame, List[pd.DataFrame]],
    targets_df: Union[pd.DataFrame, List[pd.DataFrame]],
    feature_start_time: str,
    feature_end_time: str,
    target_start_time: str,
    target_end_time: str,
    aggregation_method: Union[Callable, str] = "mean",
    min_h3_resolution: int = 0,
    leaf_h3_resolution: Union[int, None] = None,
    max_h3_resolution: int = 12,
    compute_edges: bool = True,
    make_undirected: bool = True,
    with_edge_features: bool = True,
    min_to_root_edge_distance: float = 0.0,
    include_root_node: bool = True,
    return_h3_index_to_node_id_map: bool = False,
    return_h3_index_to_aqsid_map: bool = False,
    processed_edges: Union[Tuple[List[Tuple[str, str]],
                                 List[Tuple[str, str, float]]], None] = None,
    verbose: bool = False,
) -> Union["pytorch_geometric.data.Data", Tuple["pytorch_geometric.data.Data",
                                                Dict[str, int]]]:
    """Take feature and target DataFrames and process them into a graph Data object."""
    if isinstance(features_df, pd.DataFrame):
        features_df = [features_df]
    if isinstance(targets_df, pd.DataFrame):
        targets_df = [targets_df]

    # iterate through features and targets dataframes
    for df in features_df + targets_df:
        assert "latitude" in df.columns and "longitude" in df.columns, "df must have latitude and longitude columns"
        assert "aqsid" in df.columns, "df must have aqsid column"
        assert "value" in df.columns, "df must have value column"
        assert "timestamp" in df.columns, "df must have timestamp column"
        # check that the shapes are the same
        assert df.shape == features_df[
            0].shape, "all dataframes must have the same shape"

    if verbose: print(f"[{datetime.now()}] processing graph")

    # get the leaf resolution that will give us unique hexagons for each station
    if leaf_h3_resolution is None:
        leaf_h3_resolution = determine_leaf_resolution(features_df[0],
                                                       min_h3_resolution,
                                                       max_h3_resolution,
                                                       verbose=verbose)
    if verbose:
        print(f"[{datetime.now()}] leaf resolution: {leaf_h3_resolution}")

    # process the edges and edge features
    if compute_edges:
        edges, edge_attr = process_edges(
            features_df[0], min_h3_resolution, leaf_h3_resolution,
            make_undirected, with_edge_features,
            min_to_root_edge_distance=min_to_root_edge_distance,
            include_root_node=include_root_node, verbose=verbose)
    else:
        assert processed_edges is not None, "if compute_edges is False, then processed_edges must be provided"
        edges, edge_attr = processed_edges

    if verbose: print(f"[{datetime.now()}] processed edges")

    # process the features and targets
    node_features = []
    node_targets = []
    # process the features
    for df in features_df:
        node_features.append(
            process_feature(df, feature_start_time, feature_end_time,
                            aggregation_method, min_h3_resolution,
                            leaf_h3_resolution, include_root_node,
                            verbose=verbose))
    for df in targets_df:
        node_targets.append(
            process_feature(df, target_start_time, target_end_time,
                            aggregation_method, min_h3_resolution,
                            leaf_h3_resolution, include_root_node,
                            verbose=verbose))

    if verbose: print(f"[{datetime.now()}] processed features and targets")

    # validate
    assert all([len(n) == len(node_features[0]) for n in node_features])
    assert all([len(n) == len(node_targets[0]) for n in node_targets])
    assert len(node_features[0]) == len(node_targets[0])
    assert len(edges) == len(edge_attr)
    assert all([
        n[0] == t[0] for n, t in zip(node_features[0], node_targets[0])
    ])  # make sure the node ids are the same for the nodes and targets

    # map from h3 index to node id
    h3_index_to_id_map = {v[0]: i for i, v in enumerate(node_features[0])}
    # obtain a mapping from h3 index to aqsid if needed
    h3_index_to_aqsid_map = {}
    if return_h3_index_to_aqsid_map:
        aqsid_to_h3_df = features_df[0][[
            "aqsid", "latitude", "longitude"
        ]].groupby("aqsid").first().reset_index()
        aqsid_to_h3_df["h3_index"] = aqsid_to_h3_df.apply(
            lambda x: h3.geo_to_h3(x.latitude, x.longitude, leaf_h3_resolution
                                   ), axis=1)
        h3_index_to_aqsid_map = {
            v[0]: v[1]
            for v in aqsid_to_h3_df[["h3_index", "aqsid"]].to_numpy()
        }

    if verbose: print(f"[{datetime.now()}] processed maps")

    # we can just remove the h3 index column from the nodes and targets
    node_features = np.stack(
        [v[1:].astype(np.float16) for f in node_features for v in f])
    node_targets = np.stack(
        [v[1:].astype(np.float16) for f in node_targets for v in f])

    # we need to handle missing values (negative 1) with a mask
    node_features_mask = torch.tensor(node_features >= 0, dtype=torch.bool)
    node_targets_mask = torch.tensor(node_targets >= 0, dtype=torch.bool)
    # combine the masks for an overall missingness mask
    valid_measurement_mask = torch.logical_and(node_features_mask,
                                               node_targets_mask)

    # map the edges from h3 index to node id
    edges = np.array([(h3_index_to_id_map[e[0]], h3_index_to_id_map[e[1]])
                      for e in edges]).T
    # map the edge attr from h3 index to node id
    edge_attr = np.array([e[2] for e in edge_attr], ndmin=2).T
    # make a mask for edges based on the missingness mask for the nodes

    valid_measurement_mask_edges = torch.logical_and(
        valid_measurement_mask[edges[0]], valid_measurement_mask[edges[1]])

    if verbose: print(f"[{datetime.now()}] processed masks")

    # make the graph data object
    data = Data(
        x=torch.tensor(node_features, dtype=torch.float),
        y=torch.tensor(node_targets, dtype=torch.float),
        edge_index=torch.tensor(edges, dtype=torch.long),
        edge_attr=torch.tensor(edge_attr, dtype=torch.float),
        valid_measurement_mask=valid_measurement_mask,
        valid_measurement_mask_edges=valid_measurement_mask_edges,
        node_features_mask=node_features_mask,
        node_targets_mask=node_targets_mask,
        feature_start_time=feature_start_time,
        feature_end_time=feature_end_time,
        target_start_time=target_start_time,
        target_end_time=target_end_time,
    )
    data.validate()

    if verbose: print(f"[{datetime.now()}] validated graph")

    response = [data]

    if return_h3_index_to_node_id_map:
        response.append(h3_index_to_id_map)
    if return_h3_index_to_aqsid_map:
        response.append(h3_index_to_aqsid_map)

    return response
