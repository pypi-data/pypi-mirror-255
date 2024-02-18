import unittest
from unittest.mock import patch, Mock, call
from scr.misc.utils import Utils
from scr.main.sentinel_2_band_downloader import Sentinel2_Band_Downloader

class TestSentinel2BandDownloader(unittest.TestCase):
    def setUp(self):
        # Set up any necessary objects or configurations for the tests
        self.log_path = "/path/to/output/base"
        self.output_base_path = "/path/to/output/base"
        self.sentinel2_band_downloader = Sentinel2_Band_Downloader(self.log_path, self.output_base_path)

    @patch.object(Utils, "retrieve_products_info")  # Replace 'your_module' with the actual module name
    def test_get_products_info(self, mock_retrieve_products_info):
        # Mock input data
        products = [['83dbeb41-aed4-420a-9bba-1986e9680845', 'S2A_MSIL2A_20240125T133831_N0510_R124_T22JCR_20240125T173754.SAFE', '/eodata/Sentinel-2/MSI/L2A/2024/01/25/S2A_MSIL2A_20240125T133831_N0510_R124_T22JCR_20240125T173754.SAFE','2024-01-25T18:40:14.000Z']]

        # Mock external dependencies
        mock_retrieve_products_info.return_value = [
            ["83dbeb41-aed4-420a-9bba-1986e9680845", "S2A_MSIL2A_20240125T133831_N0510_R124_T22JCR_20240125T173754", "/eodata/Sentinel-2/MSI/L2A/2024/01/25/S2A_MSIL2A_20240125T133831_N0510_R124_T22JCR_20240125T173754.SAFE", "2024-01-25T18:40:14.000Z", "T22JCR", "Sentinel-2", "L2A"]
            # Add more sample data as needed
        ]

        # Call the method under test
        result = self.sentinel2_band_downloader.get_products_info(products)

        # Now you can use 'result' directly without accessing 'return_value'
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual(result, mock_retrieve_products_info.return_value)

        # Assert that Utils.retrieve_products_info was called with the correct arguments
        mock_retrieve_products_info.assert_called_once_with(products)

if __name__ == "__main__":
    unittest.main()