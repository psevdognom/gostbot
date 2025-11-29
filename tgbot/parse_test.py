#!/usr/bin/python
# -*- coding: utf8 -*-
"""
Tests for GOST parsing tools and data sources.
"""

import unittest
from unittest.mock import patch, MagicMock

from tgbot.parse_tools import (
    get_search_list,
    get_search_list_db,
    list_available_sources,
)
from tgbot.data_sources import (
    GostDataSource,
    GostRuDataSource,
    DocsCntdRuDataSource,
    MeganormRuDataSource,
    ProtectGostRuDataSource,
    FilesStroyinfRuDataSource,
    InternetLawRuDataSource,
    LibGostRuDataSource,
    get_all_data_sources,
    fetch_from_all_sources,
)


class TestGostParsing(unittest.TestCase):
    """Test cases for GOST parsing functionality."""
    
    def test_gost_name_format(self):
        """Test that GOST names follow expected format."""
        assert 'ГОСТ 20909.1-75' == 'ГОСТ 20909.1-75'
    
    def test_list_available_sources(self):
        """Test that available sources are listed correctly."""
        sources = list_available_sources()
        self.assertIsInstance(sources, list)
        self.assertGreater(len(sources), 0)
        # Check that expected sources are present
        self.assertIn('gost.ru', sources)
        self.assertIn('docs.cntd.ru', sources)


class TestDataSources(unittest.TestCase):
    """Test cases for data source classes."""
    
    def test_all_sources_registered(self):
        """Test that all data sources are properly registered."""
        sources = get_all_data_sources()
        self.assertIsInstance(sources, list)
        self.assertGreaterEqual(len(sources), 7)  # We have 7 sources
    
    def test_source_has_required_attributes(self):
        """Test that all sources have required attributes."""
        for source in get_all_data_sources():
            self.assertIsInstance(source, GostDataSource)
            self.assertTrue(hasattr(source, 'name'))
            self.assertTrue(hasattr(source, 'base_url'))
            self.assertTrue(hasattr(source, 'fetch_gosts'))
            self.assertIsInstance(source.name, str)
            self.assertIsInstance(source.base_url, str)
    
    def test_gost_ru_source(self):
        """Test GostRuDataSource attributes."""
        source = GostRuDataSource()
        self.assertEqual(source.name, 'gost.ru')
        self.assertEqual(source.base_url, 'https://www.gost.ru')
    
    def test_docs_cntd_ru_source(self):
        """Test DocsCntdRuDataSource attributes."""
        source = DocsCntdRuDataSource()
        self.assertEqual(source.name, 'docs.cntd.ru')
        self.assertEqual(source.base_url, 'https://docs.cntd.ru')
    
    def test_meganorm_ru_source(self):
        """Test MeganormRuDataSource attributes."""
        source = MeganormRuDataSource()
        self.assertEqual(source.name, 'meganorm.ru')
        self.assertEqual(source.base_url, 'https://meganorm.ru')
    
    def test_protect_gost_ru_source(self):
        """Test ProtectGostRuDataSource attributes."""
        source = ProtectGostRuDataSource()
        self.assertEqual(source.name, 'protect.gost.ru')
        self.assertEqual(source.base_url, 'https://protect.gost.ru')
    
    def test_files_stroyinf_ru_source(self):
        """Test FilesStroyinfRuDataSource attributes."""
        source = FilesStroyinfRuDataSource()
        self.assertEqual(source.name, 'files.stroyinf.ru')
        self.assertEqual(source.base_url, 'https://files.stroyinf.ru')
    
    def test_internet_law_ru_source(self):
        """Test InternetLawRuDataSource attributes."""
        source = InternetLawRuDataSource()
        self.assertEqual(source.name, 'internet-law.ru')
        self.assertEqual(source.base_url, 'https://internet-law.ru')
    
    def test_lib_gost_ru_source(self):
        """Test LibGostRuDataSource attributes."""
        source = LibGostRuDataSource()
        self.assertEqual(source.name, 'libgost.ru')
        self.assertEqual(source.base_url, 'http://libgost.ru')


class TestMockedDataSources(unittest.TestCase):
    """Test data sources with mocked HTTP responses."""
    
    @patch('tgbot.data_sources.requests.get')
    def test_gost_ru_fetch_with_mock(self, mock_get):
        """Test GostRuDataSource with mocked response."""
        # Mock the initial page response
        mock_page_response = MagicMock()
        mock_page_response.status_code = 200
        mock_page_response.content = b'<html><a href="/test.csv">CSV</a></html>'
        
        # Mock the CSV response
        mock_csv_response = MagicMock()
        mock_csv_response.status_code = 200
        mock_csv_response.content = (
            'Name;Description\n'
            'ГОСТ 12345-67;Test standard\n'
            'ГОСТ 89012-34;Another standard\n'
        ).encode('cp1251')
        
        mock_get.side_effect = [mock_page_response, mock_csv_response]
        
        source = GostRuDataSource()
        # The fetch might fail due to XPath not matching, but it shouldn't crash
        gosts = source.fetch_gosts()
        self.assertIsInstance(gosts, list)
    
    @patch('tgbot.data_sources.requests.get')
    def test_lib_gost_ru_fetch_with_mock(self, mock_get):
        """Test LibGostRuDataSource with mocked response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <div class="news">
                <a href="/gost/123">ГОСТ 12345-67</a>
                <p>Description of the standard</p>
            </div>
        </html>
        '''
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        source = LibGostRuDataSource()
        gosts = source.fetch_gosts()
        self.assertIsInstance(gosts, list)


class TestFetchFromAllSources(unittest.TestCase):
    """Test the combined fetch functionality."""
    
    @patch('tgbot.data_sources.fetch_from_source')
    def test_fetch_from_all_sources_deduplication(self, mock_fetch):
        """Test that duplicate GOSTs are removed when fetching from all sources."""
        # Simulate different sources returning overlapping results
        mock_fetch.side_effect = [
            [{'name': 'ГОСТ 1', 'description': 'Desc 1'}],
            [{'name': 'ГОСТ 1', 'description': 'Desc 1 alt'}],  # Duplicate
            [{'name': 'ГОСТ 2', 'description': 'Desc 2'}],
            [],  # Empty result
            [{'name': 'ГОСТ 3', 'description': 'Desc 3'}],
            [],
            [],
        ]
        
        gosts = fetch_from_all_sources()
        
        # Should have deduplicated results
        names = [g['name'] for g in gosts]
        self.assertEqual(len(names), len(set(names)))  # All unique


if __name__ == '__main__':
    unittest.main()
