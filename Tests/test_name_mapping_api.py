import pytest
import json
from hca_backend.app import app
from hca_backend.OCR.name_cache import NameMatchCache

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_cache(monkeypatch, temp_cache_file):
    """Create a mock cache for testing."""
    cache = NameMatchCache(temp_cache_file)
    monkeypatch.setattr('hca_backend.app.name_cache', cache)
    return cache

def test_update_name_mapping_success(client, mock_cache):
    """Test successful name mapping update."""
    response = client.post('/update_name_mapping', json={
        'original_name': 'Test Company',
        'corrected_name': 'Test Corp Ltd',
        'entity_type': 'supplier'
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'okay'
    assert data['message'] == 'Name mapping updated successfully'
    
    # Verify cache was updated
    assert mock_cache.get('Test Company') == 'Test Corp Ltd'

def test_update_name_mapping_missing_fields(client):
    """Test name mapping update with missing fields."""
    # Test missing original_name
    response = client.post('/update_name_mapping', json={
        'corrected_name': 'Test Corp',
        'entity_type': 'supplier'
    })
    assert response.status_code == 400
    
    # Test missing corrected_name
    response = client.post('/update_name_mapping', json={
        'original_name': 'Test Company',
        'entity_type': 'supplier'
    })
    assert response.status_code == 400
    
    # Test missing entity_type
    response = client.post('/update_name_mapping', json={
        'original_name': 'Test Company',
        'corrected_name': 'Test Corp'
    })
    assert response.status_code == 400

def test_update_name_mapping_invalid_entity(client):
    """Test name mapping update with invalid entity type."""
    response = client.post('/update_name_mapping', json={
        'original_name': 'Test Company',
        'corrected_name': 'Test Corp',
        'entity_type': 'invalid_type'
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'Invalid entity type' in data['message']

def test_update_name_mapping_empty_values(client, mock_cache):
    """Test name mapping update with empty values."""
    # Test empty original name
    response = client.post('/update_name_mapping', json={
        'original_name': '',
        'corrected_name': 'Test Corp',
        'entity_type': 'supplier'
    })
    assert response.status_code == 400
    
    # Test empty corrected name
    response = client.post('/update_name_mapping', json={
        'original_name': 'Test Company',
        'corrected_name': '',
        'entity_type': 'supplier'
    })
    assert response.status_code == 400
    
    # Verify cache wasn't affected
    stats_before = mock_cache.get_stats()['total_entries']
    assert stats_before == 0

def test_update_name_mapping_persistence(client, mock_cache):
    """Test that name mapping updates persist in the cache."""
    # Make first update
    client.post('/update_name_mapping', json={
        'original_name': 'Test Company 1',
        'corrected_name': 'Test Corp 1',
        'entity_type': 'supplier'
    })
    
    # Make second update
    client.post('/update_name_mapping', json={
        'original_name': 'Test Company 2',
        'corrected_name': 'Test Corp 2',
        'entity_type': 'supplier'
    })
    
    # Verify both updates persisted
    assert mock_cache.get('Test Company 1') == 'Test Corp 1'
    assert mock_cache.get('Test Company 2') == 'Test Corp 2'
    
    # Verify stats
    stats = mock_cache.get_stats()
    assert stats['total_entries'] == 2
