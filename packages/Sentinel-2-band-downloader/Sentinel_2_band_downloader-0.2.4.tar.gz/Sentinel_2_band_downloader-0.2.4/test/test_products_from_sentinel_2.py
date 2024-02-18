import unittest
import requests
from unittest.mock import patch, MagicMock
from scr.misc.connections import Connections
from scr.main.sentinel_2_band_downloader import Sentinel2_Band_Downloader

class TestConnections(unittest.TestCase):
    @patch("scr.main.sentinel_2_band_downloader.requests.get")
    @patch("scr.misc.connections.logger")
    def test_retrieve_sent_prod_from_query_success(self, mock_connections_logger, mock_requests_get):
        # Mock the logger
        mock_connections_logger.info = MagicMock()
        mock_connections_logger.success = MagicMock()
        mock_connections_logger.warning = MagicMock()

        # Mock the requests.get response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'value': [{'Online': True}]}  # Adjust this based on your actual response structure
        mock_requests_get.return_value = mock_response

        # Instantiate Connections
        connections = Connections()

        # Test data
        params = "your_params"

        # Call the method
        result = connections.retrieve_sent_prod_from_query(params)

        # Assertions
        self.assertIsNotNone(result)
        mock_connections_logger.info.assert_called_once()
        mock_connections_logger.success.assert_called_once()
        mock_connections_logger.warning.assert_not_called()  # Ensure warning is not called
        
    @patch("scr.main.sentinel_2_band_downloader.requests.get")
    @patch("scr.misc.connections.logger")
    def test_retrieve_sent_prod_from_query_no_products(self, mock_connections_logger, mock_requests_get):
        # Mock the logger
        mock_connections_logger.info = MagicMock()
        mock_connections_logger.success = MagicMock()
        mock_connections_logger.warning = MagicMock()

        # Mock the requests.get response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'value': []}
        mock_requests_get.return_value = mock_response

        # Instantiate Connections
        connections = Connections()

        # Test data
        params = "your_params"

        # Call the method
        result = connections.retrieve_sent_prod_from_query(params)

        # Assertions
        self.assertIsNone(result)
        self.assertTrue(mock_connections_logger.info.called)
        self.assertFalse(mock_connections_logger.success.called)
        self.assertTrue(mock_connections_logger.warning.called)

    @patch("scr.main.sentinel_2_band_downloader.requests.get")
    @patch("scr.misc.connections.logger")
    def test_retrieve_sent_prod_from_query_error(self, mock_connections_logger, mock_requests_get):
        # Mock the logger
        mock_connections_logger.info = MagicMock()
        mock_connections_logger.success = MagicMock()
        mock_connections_logger.warning = MagicMock()


        # Mock the requests.get response for an error status code
        mock_response = MagicMock()
        mock_response.status_code = 500  # Example: Internal Server Error
        mock_requests_get.return_value = mock_response

        # Instantiate Connections
        connections = Connections()

        # Test data
        params = "your_params"
        try:
            connections.retrieve_sent_prod_from_query(params)
        except requests.exceptions.HTTPError as e:
            print(f"HTTPError raised: {e}")
            raise e  # Re-raise the exception for further inspection
        except Exception as e:
            print(f"Unexpected exception raised: {e}")
            # If you're seeing this, it means an unexpected exception was raised
            raise e

        # Assertions
        self.assertTrue(mock_connections_logger.info.called)
        self.assertFalse(mock_connections_logger.success.called)
        self.assertFalse(mock_connections_logger.warning.called)

if __name__ == '__main__':
    unittest.main()