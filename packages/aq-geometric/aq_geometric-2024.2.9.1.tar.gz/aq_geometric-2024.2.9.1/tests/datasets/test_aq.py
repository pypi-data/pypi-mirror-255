import unittest
from unittest.mock import patch
from datetime import datetime
import pandas as pd
import numpy as np
import os
import os.path as osp
import torch
from aq_geometric.data.aq import load_hourly_data, load_stations_info, process_df, determine_leaf_resolution, process_edges


class TestDataFunctions(unittest.TestCase):
    @patch("aq_geometric.data.aq.get_engine")
    def test_load_hourly_data(self, mock_get_engine):
        # Mock the engine and test the function
        mock_engine = mock_get_engine.return_value
        df = load_hourly_data(mock_engine, table_name="hourly_data",
                              features=["PM2.5"], start_date="2020-01-01",
                              end_date="2024-01-01", aqsid=["12345"],
                              verbose=False)

        # Assert the expected output
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (10, 5))  # Assuming 10 rows and 5 columns

        # Add more assertions as needed

    @patch("aq_geometric.data.aq.get_engine")
    def test_load_stations_info(self, mock_get_engine):
        # Mock the engine and test the function
        mock_engine = mock_get_engine.return_value
        df = load_stations_info(mock_engine, table_name="stations_info",
                                query_date="2022-01-01", aqsid=["12345"],
                                verbose=False)

        # Assert the expected output
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape, (5, 4))  # Assuming 5 rows and 4 columns

        # Add more assertions as needed

    def test_process_df(self):
        # Create dummy data for testing
        df = pd.DataFrame({
            "aqsid": ["12345", "67890"],
            "timestamp": ["2020-01-01 00:00:00", "2020-01-01 01:00:00"],
            "value": [10, 20]
        })
        stations_info = pd.DataFrame({
            "aqsid": ["12345", "67890"],
            "latitude": [40.0, 41.0],
            "longitude": [-75.0, -76.0],
            "elevation": [100, 200]
        })

        processed_df = process_df(df, stations_info, start_time="2020-01-01",
                                  end_time="2020-01-01", time_step="1H",
                                  aggregation_method="mean", nan_value=-1,
                                  verbose=False)

        # Assert the expected output
        self.assertIsInstance(processed_df, pd.DataFrame)
        self.assertEqual(processed_df.shape,
                         (2, 6))  # Assuming 2 rows and 6 columns

        # Add more assertions as needed

    def test_determine_leaf_resolution(self):
        # Create dummy data for testing
        df = pd.DataFrame({
            "latitude": [40.0, 41.0, 42.0],
            "longitude": [-75.0, -76.0, -77.0],
            "aqsid": ["12345", "67890", "54321"]
        })

        leaf_resolution = determine_leaf_resolution(df, min_h3_resolution=0,
                                                    max_h3_resolution=12,
                                                    verbose=False)

        # Assert the expected output
        self.assertEqual(leaf_resolution, 5)  # Assuming leaf resolution is 5

        # Add more assertions as needed

    def test_process_edges(self):
        # Create dummy data for testing
        df = pd.DataFrame({
            "latitude": [40.0, 41.0, 42.0],
            "longitude": [-75.0, -76.0, -77.0],
            "aqsid": ["12345", "67890", "54321"]
        })

        edges = process_edges(df, min_h3_resolution=0, leaf_h3_resolution=5,
                              make_undirected=True, with_edge_features=True,
                              min_to_root_edge_distance=0.0,
                              include_root_node=True, verbose=False)

        # Assert the expected output
        self.assertIsInstance(edges, list)
        self.assertEqual(len(edges), 6)  # Assuming 6 edges

        # Add more assertions as needed


class TestProcess(unittest.TestCase):
    def test_process(self):
        # Create dummy data for testing
        data_fp = "/path/to/data.csv"
        stations_info_fp = "/path/to/stations_info.csv"
        processed_dir = "/path/to/processed"
        raw_file_names = [data_fp, stations_info_fp]
        start_time = "2020-01-01"
        end_time = "2020-01-02"
        sample_freq = "1H"
        nan_value = -1
        min_h3_resolution = 0
        max_h3_resolution = 12
        make_undirected = True
        with_edge_features = True
        min_to_root_edge_distance = 0.0
        include_root_node = True
        verbose = False

        # Mock the necessary functions
        with patch("aq_geometric.data.aq.load_hourly_data_from_fp") as mock_load_hourly_data_from_fp, \
             patch("aq_geometric.data.aq.load_stations_info_from_fp") as mock_load_stations_info_from_fp, \
             patch("aq_geometric.data.aq.process_df") as mock_process_df, \
             patch("aq_geometric.data.aq.determine_leaf_resolution") as mock_determine_leaf_resolution, \
             patch("aq_geometric.data.aq.process_edges") as mock_process_edges, \
             patch("aq_geometric.data.aq.process_graph") as mock_process_graph, \
             patch("os.makedirs") as mock_makedirs, \
             patch("os.path.exists") as mock_exists, \
             patch("torch.save") as mock_torch_save:

            # Set the return values for the mocked functions
            mock_exists.return_value = False
            mock_load_hourly_data_from_fp.return_value = pd.DataFrame({
                "aqsid": ["12345", "67890"],
                "timestamp": ["2020-01-01 00:00:00", "2020-01-01 01:00:00"],
                "value": [10, 20]
            })
            mock_load_stations_info_from_fp.return_value = pd.DataFrame({
                "aqsid": ["12345", "67890"],
                "latitude": [40.0, 41.0],
                "longitude": [-75.0, -76.0],
                "elevation": [100, 200]
            })
            mock_process_df.return_value = pd.DataFrame({
                "aqsid": ["12345", "67890"],
                "timestamp": ["2020-01-01 00:00:00", "2020-01-01 01:00:00"],
                "value": [10, 20]
            })
            mock_determine_leaf_resolution.return_value = 5
            mock_process_edges.return_value = ([1, 2, 3], [4, 5, 6])
            mock_process_graph.return_value = ("graph",
                                               "h3_index_to_node_id_map",
                                               "h3_index_to_aqsid_map")

            # Create an instance of the class
            obj = Process(data_fp, stations_info_fp, processed_dir,
                          raw_file_names, start_time, end_time, sample_freq,
                          nan_value, min_h3_resolution, max_h3_resolution,
                          make_undirected, with_edge_features,
                          min_to_root_edge_distance, include_root_node,
                          verbose)

            # Call the process method
            obj.process()

            # Assert the expected function calls
            mock_makedirs.assert_called_once_with(processed_dir)
            mock_exists.assert_called_once_with(processed_dir)
            mock_load_hourly_data_from_fp.assert_called_once_with(data_fp)
            mock_load_stations_info_from_fp.assert_called_once_with(
                stations_info_fp)
            mock_process_df.assert_called_once_with(
                pd.DataFrame({
                    "aqsid": ["12345", "67890"],
                    "timestamp":
                    ["2020-01-01 00:00:00", "2020-01-01 01:00:00"],
                    "value": [10, 20]
                }),
                pd.DataFrame({
                    "aqsid": ["12345", "67890"],
                    "latitude": [40.0, 41.0],
                    "longitude": [-75.0, -76.0],
                    "elevation": [100, 200]
                }), "2020-01-01", "2020-01-02", "1H", nan_value=-1,
                verbose=False)
            mock_determine_leaf_resolution.assert_called_once_with(
                pd.DataFrame({
                    "aqsid": ["12345", "67890"],
                    "timestamp":
                    ["2020-01-01 00:00:00", "2020-01-01 01:00:00"],
                    "value": [10, 20]
                }), 0, 12, verbose=False)
            mock_process_edges.assert_called_once_with(
                pd.DataFrame({
                    "aqsid": ["12345", "67890"],
                    "timestamp":
                    ["2020-01-01 00:00:00", "2020-01-01 01:00:00"],
                    "value": [10, 20]
                }), 0, 5, True, True, 0.0, True, verbose=False)
            mock_process_graph.assert_called_once_with(
                features_df=[
                    pd.DataFrame({
                        "aqsid": ["12345", "67890"],
                        "timestamp":
                        ["2020-01-01 00:00:00", "2020-01-01 01:00:00"],
                        "value": [10, 20]
                    })
                ], targets_df=[
                    pd.DataFrame({
                        "aqsid": ["12345", "67890"],
                        "timestamp":
                        ["2020-01-01 00:00:00", "2020-01-01 01:00:00"],
                        "value": [10, 20]
                    })
                ], feature_start_time="2020-01-01",
                feature_end_time="2020-01-01", target_start_time="2020-01-01",
                target_end_time="2020-01-01", aggregation_method=mock.ANY,
                min_h3_resolution=0, leaf_h3_resolution=5,
                max_h3_resolution=12, include_root_node=True,
                compute_edges=False, make_undirected=True,
                with_edge_features=True, min_to_root_edge_distance=0.0,
                return_h3_index_to_node_id_map=True,
                return_h3_index_to_aqsid_map=True,
                processed_edges=([1, 2, 3], [4, 5, 6]), verbose=False)
            mock_torch_save.assert_called_with(
                "h3_index_to_node_id_map",
                osp.join(processed_dir, "h3_index_to_node_id_map.pt"))
            mock_torch_save.assert_called_with(
                "h3_index_to_aqsid_map",
                osp.join(processed_dir, "h3_index_to_aqsid_map.pt"))
            mock_torch_save.assert_called_with(
                "graph", osp.join(processed_dir, "data_0.pt"))
