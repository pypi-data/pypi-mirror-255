import os.path as osp
from typing import Tuple, List, Union, Callable

import torch
import numpy as np
import pandas as pd
from torch_geometric.data import Dataset

from aq_geometric.data import load_hourly_data, load_stations_info, load_hourly_data_from_fp, load_stations_info_from_fp, process_df, process_graph, process_edges, determine_leaf_resolution
from aq_utilities.engine.psql import get_engine


class AqGraphDataset(Dataset):
    r"""The AQ Graph dataset from the database.

    Args:
        root (string): Root directory where the dataset should be saved.
        engine (string, optional): SQLAlchemy connection string.
        transform (callable, optional): A function/transform that takes in an
            :obj:`torch_geometric.data.Data` object and returns a transformed
            version. The data object will be transformed before every access.
            (default: :obj:`None`)
        pre_transform (callable, optional): A function/transform that takes in
            an :obj:`torch_geometric.data.Data` object and returns a
            transformed version. The data object will be transformed before
            being saved to disk. (default: :obj:`None`)
        start_time (string, optional): Start time for the features.
        end_time (string, optional): End time for the features.
        sample_freq (string, optional): Sample frequency for the features.  
        samples_in_node_feature (int, optional): Number of samples in the node feature.
        aggregation_method (callable, optional): Aggregation method for the features.
            default is :obj:`lambda x: np.mean(x[x >= 0]) if len(x[x >= 0]) > 0 else -1`.
        nan_value (float, optional): Value to use for missing measurements.
        min_h3_resolution (int, optional): Minimum H3 resolution default is 0.
        max_h3_resolution (int, optional): Maximum H3 resolution default is 12.
        include_root_node (bool, optional): Whether to include the root node.
        compute_edges (bool, optional): Whether to compute the edges.
        make_undirected (bool, optional): Whether to make the edges undirected.
        with_edge_features (bool, optional): Whether to compute edge features.
        min_to_root_edge_distance (float, optional): Distance for the edge to the root node.
        verbose (bool, optional): Whether to print verbose output.
    """
    def __init__(
        self,
        root,
        engine=None,
        transform=None,
        pre_transform=None,
        pre_filter=None,
        start_time="2020-01-01",
        end_time="2024-01-01",
        sample_freq="1H",
        aqsids: Union[List[str], None] = None,
        samples_in_node_feature=8,
        aggregation_method=lambda x: np.mean(x[x >= 0])
        if len(x[x >= 0]) > 0 else -1,
        nan_value=-1,
        min_h3_resolution=0,
        max_h3_resolution=12,
        include_root_node=True,
        compute_edges=True,
        make_undirected=True,
        with_edge_features=True,
        min_to_root_edge_distance=0.0,
        verbose=False,
    ):
        if engine is None:
            engine = get_engine()
        self.engine = engine
        self.start_time = start_time
        self.end_time = end_time
        self.sample_freq = sample_freq
        self.aqsids = aqsids
        self.samples_in_node_feature = samples_in_node_feature
        self.aggregation_method = aggregation_method
        self.nan_value = nan_value
        self.min_h3_resolution = min_h3_resolution
        self.max_h3_resolution = max_h3_resolution
        self.include_root_node = include_root_node
        self.compute_edges = compute_edges
        self.make_undirected = make_undirected
        self.with_edge_features = with_edge_features
        self.min_to_root_edge_distance = min_to_root_edge_distance
        self.verbose = verbose
        super().__init__(root, transform, pre_transform, pre_filter)

    @property
    def raw_file_names(self) -> Tuple[str, str]:
        """Return the raw file name of the data and stations info."""
        return (osp.join(self.raw_dir, "data.csv"),
                osp.join(self.raw_dir, "stations_info.csv"))

    @property
    def processed_file_names(self) -> List[str]:
        """Return the processed file names."""
        from glob import glob
        return [
            osp.basename(f)
            for f in glob(osp.join(self.processed_dir, "data_*.pt"))
        ]

    def clear(self):
        """Clear the raw and processed directories."""
        import shutil
        shutil.rmtree(self.raw_dir)
        shutil.rmtree(self.processed_dir)

    def download(self):
        """Query remote database for the data and stations info, saving to csv files."""
        # check if the path exists
        if not osp.exists(self.raw_dir):
            os.makedirs(self.raw_dir)
        # check that the data and stations info files do not exist
        if osp.exists(osp.join(self.raw_dir, "data.csv")) and osp.exists(
                osp.join(self.raw_dir, "stations_info.csv")):
            return
        # get the data from the database
        df = load_hourly_data(engine=self.engine, start_date=self.start_time,
                              end_date=self.end_time, aqsid=self.aqsids,
                              verbose=self.verbose)
        # get the station information for these stations from the database
        df_stations = load_stations_info(
            engine=self.engine, aqsid=self.aqsids,
            verbose=self.verbose)  # @TODO add query_date=self.start_time,
        # save the data to a csv file
        df.to_csv(osp.join(self.raw_dir, "data.csv"), index=False)
        df_stations.to_csv(osp.join(self.raw_dir, "stations_info.csv"),
                           index=False)

    def process(self):
        """Process the data and stations info into individual graphs."""
        # ensure the processed directory exists
        if not osp.exists(self.processed_dir):
            os.makedirs(self.processed_dir)
        # check if the there are already processed files
        if len(self.processed_file_names) > 0:
            return
        data_fp, stations_info_fp = self.raw_file_names
        # load the data and stations info
        data = load_hourly_data_from_fp(data_fp)
        stations_info = load_stations_info_from_fp(stations_info_fp)
        # process the data and stations info
        df = process_df(data, stations_info, self.start_time, self.end_time,
                        self.sample_freq, nan_value=self.nan_value,
                        verbose=self.verbose)
        # determine the leaf resolution
        leaf_resolution = determine_leaf_resolution(df, self.min_h3_resolution,
                                                    self.max_h3_resolution,
                                                    self.verbose)
        # process the edges and edge features once as they are the same for all graphs
        edges, edge_attr = process_edges(df, self.min_h3_resolution,
                                         leaf_resolution, self.make_undirected,
                                         self.with_edge_features,
                                         self.min_to_root_edge_distance,
                                         self.include_root_node, self.verbose)

        # obtain the timestamps for the features and targets
        timestamps = pd.date_range(start=df.timestamp.min(),
                                   end=df.timestamp.max(),
                                   freq=self.sample_freq)
        # take every timestamp up to the nth timestamp
        feature_start_time = timestamps[:-1]
        # take every timestamp, starting at the nth timestamp, up to the last timestamp
        feature_end_time = timestamps[:-1]
        # take every timestamp, starting at the (n+1)th timestamp
        target_start_time = timestamps[1:]

        self.start_time = feature_start_time[0]
        self.end_time = target_start_time[-1]

        # ensure that the lengths are the same
        if len(feature_start_time) > len(target_start_time):
            if len(feature_start_time) == len(feature_end_time):
                feature_start_time = feature_start_time[:-1]
                feature_end_time = feature_end_time[:-1]
            else:
                feature_start_time = feature_start_time[:-1]

        for i, (feature_start_time, feature_end_time,
                target_start_time) in enumerate(
                    zip(feature_start_time, feature_end_time,
                        target_start_time)):
            graph, h3_index_to_node_id_map, h3_index_to_aqsid_map = process_graph(
                features_df=[df],
                targets_df=[df],
                feature_start_time=feature_start_time,
                feature_end_time=feature_end_time,
                target_start_time=target_start_time,
                target_end_time=target_start_time,
                aggregation_method=lambda x: np.mean(x[x >= 0])
                if len(x[x >= 0]) > 0 else -1,
                min_h3_resolution=self.min_h3_resolution,
                leaf_h3_resolution=leaf_resolution,
                max_h3_resolution=self.
                max_h3_resolution,  # this is ignored if leaf_h3_resolution is not None
                include_root_node=self.include_root_node,
                compute_edges=False,
                make_undirected=
                True,  # this is ignored if compute_edges is False
                with_edge_features=
                True,  # this is ignored if compute_edges is False
                min_to_root_edge_distance=
                0.0,  # this is ignored if compute_edges is False
                return_h3_index_to_node_id_map=True,
                return_h3_index_to_aqsid_map=True,
                processed_edges=(edges, edge_attr),
                verbose=self.verbose,
            )
            if self.verbose:
                print(f"Processed graph {i+1} of {len(timestamps)}")
            if self.verbose:
                print(
                    f"Graph feature start time {feature_start_time}, feature end time {feature_end_time}, and end time {target_start_time}"
                )

            # save the h3_index_to_id_map if one does not exist
            if not osp.exists(
                    osp.join(self.processed_dir,
                             "h3_index_to_node_id_map.pt")):
                torch.save(
                    h3_index_to_node_id_map,
                    osp.join(self.processed_dir, "h3_index_to_node_id_map.pt"))
            # do the same for the h3_index_to_aqsid_map
            if not osp.exists(
                    osp.join(self.processed_dir, "h3_index_to_aqsid_map.pt")):
                torch.save(
                    h3_index_to_aqsid_map,
                    osp.join(self.processed_dir, "h3_index_to_aqsid_map.pt"))

            if self.pre_filter is not None and not self.pre_filter(graph):
                continue

            if self.pre_transform is not None:
                data = self.pre_transform(graph)

            torch.save(graph, osp.join(self.processed_dir, f'data_{i}.pt'))

    def len(self):
        return len(self.processed_file_names) - self.samples_in_node_feature

    def get(self, idx):
        # data is a PyG Data object
        data = torch.load(osp.join(self.processed_dir, f'data_{idx}.pt'))
        num_features_used = 1
        for i in range(num_features_used, self.samples_in_node_feature):
            # we need to concatenate the node features, edge features are unchanged
            new_graph = torch.load(
                osp.join(self.processed_dir, f'data_{idx+i}.pt'))
            data.x = torch.cat([data.x, new_graph.x], dim=1)
        # we need to set the target to the last graph's target
        if self.samples_in_node_feature > 1:
            data.y = new_graph.y
        return data
