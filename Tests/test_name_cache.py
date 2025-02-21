import pytest
import os
import tempfile
import json
from hca_backend.OCR.name_cache import NameMatchCache

class TestNameCache:

    @pytest.fixture
    def temp_cache_file(self):
        """Creates a temporary file for caching and yields its file path."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            yield f.name
        os.unlink(f.name)

    @pytest.fixture
    def cache(self, temp_cache_file):
        """Initializes and returns a NameMatchCache instance using the provided temporary cache file."""
        return NameMatchCache(temp_cache_file)

    def test_normalize_name(self, cache):
        """Test name normalization."""
        test_cases = [('Rachit Fashion Pvt Ltd', 'rachitfashion'), ('V.K. FABRICS', 'vkfabrics'), ('Samunder Saree Center (D.K)', 'samundersareecenterdk'), ('', ''), (None, '')]
        for (input_name, expected) in test_cases:
            assert cache._normalize_name(input_name) == expected

    def test_cache_operations(self, cache):
        """Test basic cache operations."""
        cache.set('Rachit Fashion', 'Rachit Fashion Pvt Ltd')
        assert cache.get('Rachit Fashion') == 'Rachit Fashion Pvt Ltd'
        assert cache.get('RACHIT FASHION') == 'Rachit Fashion Pvt Ltd'
        assert cache.get('Rachit Fashon') == 'Rachit Fashion Pvt Ltd'
        assert cache.get('Nonexistent Name') is None

    def test_cache_persistence(self, temp_cache_file):
        """Test that cache persists between instances."""
        cache1 = NameMatchCache(temp_cache_file)
        cache1.set('Test Name', 'Matched Name')
        cache2 = NameMatchCache(temp_cache_file)
        assert cache2.get('Test Name') == 'Matched Name'

    def test_cache_stats(self, cache):
        """Test cache statistics."""
        stats = cache.get_stats()
        assert stats['total_entries'] == 0
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['hit_ratio'] == 0
        cache.set('name1', 'match1')
        cache.set('name2', 'match2')
        cache.get('name1')
        cache.get('name2')
        cache.get('name3')
        stats = cache.get_stats()
        assert stats['total_entries'] == 2
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['hit_ratio'] == 2 / 3

    def test_fuzzy_matching(self, cache):
        """Test fuzzy matching in cache."""
        cache.set('V.K. Fabrics Pvt Ltd', 'V.K. Fabrics Private Limited')
        variations = ['V K Fabrics', 'VK Fabrics', 'V.K Fabrics', 'V.K. Fabrics Limited']
        for variant in variations:
            assert cache.get(variant) == 'V.K. Fabrics Private Limited'

    def test_empty_inputs(self, cache):
        """Test handling of empty or None inputs."""
        cache.set('', 'Some Value')
        cache.set(None, 'Some Value')
        cache.set('Valid Name', '')
        cache.set('Valid Name', None)
        assert cache.get('') is None
        assert cache.get(None) is None
        stats = cache.get_stats()
        assert stats['total_entries'] == 0

    def test_nonexistent_cache_file(self):
        """Test initialization with a non-existent cache file in a non-existent directory."""
        test_dir = os.path.join(tempfile.gettempdir(), 'nonexistent_dir')
        cache_file = os.path.join(test_dir, 'cache.json')
        if os.path.exists(test_dir):
            os.rmdir(test_dir)
        cache = NameMatchCache(cache_file)
        assert os.path.exists(test_dir)
        assert os.path.exists(cache_file)
        cache.set('Test Name', 'Matched Name')
        assert cache.get('Test Name') == 'Matched Name'
        with open(cache_file, 'r') as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert len(data) == 1
        os.unlink(cache_file)
        os.rmdir(test_dir)

    def test_update_mapping(self, cache):
        """Test the update_mapping functionality for human corrections."""
        cache.update_mapping('Original Name', 'Corrected Name')
        assert cache.get('Original Name') == 'Corrected Name'
        cache.update_mapping('Original Name Ltd', 'Corrected Name')
        assert cache.get('Original Name') == 'Corrected Name'
        assert cache.get('Original Name Ltd') == 'Corrected Name'
        cache.update_mapping('', 'Some Name')
        cache.update_mapping('Some Name', '')
        cache.update_mapping(None, 'Some Name')
        assert cache.get('') is None
        assert cache.get(None) is None
        stats_before = cache.get_stats()['total_entries']
        cache.update_mapping('New Test Name', 'New Corrected Name')
        stats_after = cache.get_stats()['total_entries']
        assert stats_after == stats_before + 1
        assert cache.get('New Test Name') == 'New Corrected Name'