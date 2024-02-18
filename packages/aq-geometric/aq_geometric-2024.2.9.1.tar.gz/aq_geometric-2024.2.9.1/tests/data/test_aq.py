import unittest
from unittest.mock import patch
from datetime import datetime
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


if __name__ == "__main__":
    unittest.main()
