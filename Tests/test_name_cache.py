import pytest
import os
import tempfile
import json
from hca_backend.OCR.name_cache import NameMatchCache

class TestNameCache:
    @pytest.fixture
    def temp_cache_file(self):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            yield f.name
        os.unlink(f.name)  # Cleanup after test

    @pytest.fixture
    def cache(self, temp_cache_file):
        return NameMatchCache(temp_cache_file)

    def test_normalize_name(self, cache):
        """Test name normalization."""
        test_cases = [
            ("Rachit Fashion Pvt Ltd", "rachitfashion"),
            ("V.K. FABRICS", "vkfabrics"),
            ("Samunder Saree Center (D.K)", "samundersareecenterdk"),
            ("", ""),
            (None, "")
        ]
        
        for input_name, expected in test_cases:
            assert cache._normalize_name(input_name) == expected

    def test_cache_operations(self, cache):
        """Test basic cache operations."""
        # Test set and get
        cache.set("Rachit Fashion", "Rachit Fashion Pvt Ltd")
        assert cache.get("Rachit Fashion") == "Rachit Fashion Pvt Ltd"
        
        # Test case insensitive
        assert cache.get("RACHIT FASHION") == "Rachit Fashion Pvt Ltd"
        
        # Test fuzzy matching
        assert cache.get("Rachit Fashon") == "Rachit Fashion Pvt Ltd"
        
        # Test non-existent
        assert cache.get("Nonexistent Name") is None

    def test_cache_persistence(self, temp_cache_file):
        """Test that cache persists between instances."""
        # First instance
        cache1 = NameMatchCache(temp_cache_file)
        cache1.set("Test Name", "Matched Name")
        
        # Second instance should load the saved data
        cache2 = NameMatchCache(temp_cache_file)
        assert cache2.get("Test Name") == "Matched Name"

    def test_cache_stats(self, cache):
        """Test cache statistics."""
        # Initial stats
        stats = cache.get_stats()
        assert stats["total_entries"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_ratio"] == 0
        
        # Add some entries and do some lookups
        cache.set("name1", "match1")
        cache.set("name2", "match2")
        
        cache.get("name1")  # Hit
        cache.get("name2")  # Hit
        cache.get("name3")  # Miss
        
        stats = cache.get_stats()
        assert stats["total_entries"] == 2
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_ratio"] == 2/3

    def test_fuzzy_matching(self, cache):
        """Test fuzzy matching in cache."""
        cache.set("V.K. Fabrics Pvt Ltd", "V.K. Fabrics Private Limited")
        
        # These should all match
        variations = [
            "V K Fabrics",
            "VK Fabrics",
            "V.K Fabrics",
            "V.K. Fabrics Limited"
        ]
        
        for variant in variations:
            assert cache.get(variant) == "V.K. Fabrics Private Limited"

    def test_empty_inputs(self, cache):
        """Test handling of empty or None inputs."""
        # Setting empty values
        cache.set("", "Some Value")  # Should not be stored
        cache.set(None, "Some Value")  # Should not be stored
        cache.set("Valid Name", "")  # Should not be stored
        cache.set("Valid Name", None)  # Should not be stored
        
        # Getting empty values
        assert cache.get("") is None
        assert cache.get(None) is None
        
        # Check that invalid sets didn't affect stats
        stats = cache.get_stats()
        assert stats["total_entries"] == 0

    def test_nonexistent_cache_file(self):
        """Test initialization with a non-existent cache file in a non-existent directory."""
        # Create path to a file in a non-existent directory
        test_dir = os.path.join(tempfile.gettempdir(), "nonexistent_dir")
        cache_file = os.path.join(test_dir, "cache.json")
        
        # Ensure directory and file don't exist
        if os.path.exists(test_dir):
            os.rmdir(test_dir)
            
        # Initialize cache with non-existent path
        cache = NameMatchCache(cache_file)
        
        # Verify directory and file were created
        assert os.path.exists(test_dir)
        assert os.path.exists(cache_file)
        
        # Verify cache operations work
        cache.set("Test Name", "Matched Name")
        assert cache.get("Test Name") == "Matched Name"
        
        # Verify file contains valid JSON
        with open(cache_file, 'r') as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert len(data) == 1
        
        # Cleanup
        os.unlink(cache_file)
        os.rmdir(test_dir)
