import unittest
from unittest.mock import patch, Mock
from scr.misc.utils import Utils
from scr.main.sentinel_2_band_downloader import Sentinel2_Band_Downloader

class TestSentinel2BandDownloader(unittest.TestCase):
    def setUp(self):
        self.log_path = "/path/to/output/base" 
        self.output_path = "/path/to/output/base"
        self.downloader = Sentinel2_Band_Downloader(self.log_path, self.output_path)

    @patch.object(Utils, "construct_query_for_sentinel2_products")  # Correct mocking target
    def test_construct_query_string_type(self, mock_query):

        # Test data
        footprint = "your_footprint"
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        cloud_cover_percentage = "20"
        type = "your_type"
        platform_name = 'SENTINEL-2'
        
        # Set up the return value for the mock
        expected_query = (
            f"?&$filter=(Collection/Name%20eq%20%27{platform_name}%27%20and%20"
            f"(Attributes/OData.CSC.StringAttribute/any(att:att/Name%20eq%20%27instrumentShortName%27%20and%20"
            f"att/OData.CSC.StringAttribute/Value%20eq%20%27MSI%27)%20and%20"
            f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name%20eq%20%27cloudCover%27%20and%20"
            f"att/OData.CSC.DoubleAttribute/Value%20le%2070)%20and%20"
            f"(contains(Name,%27{type}%27)%20and%20"
            f"OData.CSC.Intersects(area=geography%27SRID=4326;{footprint}%27)))%20and%20Online%20eq%20true)%20and%20"
            f"ContentDate/Start%20ge%20{start_date}T00:00:00.000Z%20and%20"
            f"ContentDate/Start%20lt%20{end_date}T23:59:59.999Z&$orderby=ContentDate/Start%20desc&"
            f"$expand=Attributes&$count=True&$top=50&$expand=Assets&$skip=0"
        )
        mock_query.return_value = expected_query

        # Call the method
        result = self.downloader.construct_query(footprint, start_date, end_date, cloud_cover_percentage, type, platform_name)

        # Set self.maxDiff to None to see the entire diff
        self.maxDiff = None

        # Assertions
        self.assertEqual(result, expected_query)

        # Set up the return value for the mock
        expected_query = (
            f"?&$filter=(Collection/Name%20eq%20%27{platform_name}%27%20and%20"
            f"(Attributes/OData.CSC.StringAttribute/any(att:att/Name%20eq%20%27instrumentShortName%27%20and%20"
            f"att/OData.CSC.StringAttribute/Value%20eq%20%27MSI%27)%20and%20"
            f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name%20eq%20%27cloudCover%27%20and%20"
            f"att/OData.CSC.DoubleAttribute/Value%20le%2066)%20and%20"
            f"((contains(Name,%27{type[0]}%27)%20and%20"
            f"OData.CSC.Intersects(area=geography%27SRID=4326;{footprint}%27))%20or%20"
            f"(contains(Name,%27{type[1]}%27)%20and%20"
            f"OData.CSC.Intersects(area=geography%27SRID=4326;{footprint}%27))))%20and%20"
            f"Online%20eq%20true)%20and%20ContentDate/Start%20ge%20{start_date}T00:00:00.000Z%20and%20"
            f"ContentDate/Start%20lt%20{end_date}T23:59:59.999Z&$orderby=ContentDate/Start%20desc&"
            f"$expand=Attributes&$count=True&$top=50&$expand=Assets&$skip=0"
        )
        mock_query.return_value = expected_query

        # Call the method
        result = self.downloader.construct_query(footprint, start_date, end_date, cloud_cover_percentage, type, platform_name)

        # Set self.maxDiff to None to see the entire diff
        self.maxDiff = None

        # Assertions
        self.assertEqual(result, expected_query)

if __name__ == '__main__':
    unittest.main()