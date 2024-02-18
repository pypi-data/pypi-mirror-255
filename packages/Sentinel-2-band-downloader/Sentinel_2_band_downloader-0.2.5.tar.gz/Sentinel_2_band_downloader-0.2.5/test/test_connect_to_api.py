import unittest
import requests
from unittest.mock import patch
from scr.misc.connections import Connections
from scr.main.sentinel_2_band_downloader import Sentinel2_Band_Downloader

class TestSentinel2BandDownloader(unittest.TestCase):
    def setUp(self):
        self.log_path = "/path/to/output/base" 
        self.output_path = "/path/to/output/base"
        self.downloader = Sentinel2_Band_Downloader(self.log_path, self.output_path)
    
    @patch.object(Connections, "access_token")
    def test_connect_to_api_success(self, mock_access_token):
        mock_access_token.return_value = "valid_access_token"
        username = "test_user"
        password = "test_password"

        access_token = self.downloader.connect_to_api(username, password)

        mock_access_token.assert_called_once_with(username, password)
        self.assertEqual(access_token, "valid_access_token")
        
    @patch.object(Connections, "access_token")
    def test_connect_to_api_invalid_credentials(self, mock_access_token):
        mock_access_token.side_effect = Exception("Invalid credentials")
        username = "wrong_user"
        password = "wrong_password"

        with self.assertRaises(Exception) as context:
            self.downloader.connect_to_api(username, password)

        self.assertEqual(str(context.exception), "Invalid credentials")

    @patch.object(Connections, "access_token")
    def test_connect_to_api_network_error(self, mock_access_token):
        mock_access_token.side_effect = requests.exceptions.ConnectionError
        username = "any_user"
        password = "any_password"

        with self.assertRaises(requests.exceptions.ConnectionError):
            self.downloader.connect_to_api(username, password)
            




