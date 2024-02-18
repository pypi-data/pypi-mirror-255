import unittest
from unittest.mock import patch, Mock, call
from scr.misc.files import Files
from scr.main.sentinel_2_band_downloader import Sentinel2_Band_Downloader

class TestSentinel2BandDownloader(unittest.TestCase):
    def setUp(self):
        # Set up any necessary objects or configurations for the tests
        self.log_path = "/path/to/output/base"
        self.output_base_path = "/path/to/output/base"
        self.sentinel2_band_downloader = Sentinel2_Band_Downloader(self.log_path, self.output_base_path)

    @patch.object(Files, "create_output_folders")
    def test_output_folder(self, mock_create_output_folders):
        # Mock input data
        products_info = [["id1", "name1", "path1", "2024-01-25T18:40:14.000Z", "tile1", "platform1", "L1C"]]
        bands_dict = {
            "L1C": ["band1", "band2"],
            "L2A": {"resolution10m": ["band3", "band4"], "resolution20m": ["band5", "band6"]},
        }

        # Mock the return value of create_output_folders
        mock_create_output_folders.return_value = ['/mocked/directory1', '/mocked/directory2']

        # Call the method under test
        directory_paths = self.sentinel2_band_downloader.output_folder(products_info, bands_dict)

        # Assert the expected output
        self.assertIsInstance(directory_paths, list)
        self.assertGreater(len(directory_paths), 0)


if __name__ == "__main__":
    unittest.main()