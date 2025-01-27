import pytest
import os
import tempfile
from Individual import Supplier, Party
from hca_backend.OCR.name_cache import NameMatchCache

@pytest.fixture
def temp_cache_dir():
    """Create a temporary directory for cache files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def temp_cache_file(temp_cache_dir):
    """Create a temporary cache file path."""
    return os.path.join(temp_cache_dir, "test_cache.json")

@pytest.fixture
def mock_cache(temp_cache_file):
    """Create a mock cache instance with temporary file."""
    cache = NameMatchCache(temp_cache_file)
    return cache

def pytest_sessionstart(session): 
    """Runs before whole test starts"""
    pass

def pytest_sessionfinish(session, exitstatus):
    """whole test run finishes."""
    pass
