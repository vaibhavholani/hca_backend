import pytest
import json
import base64
import io
from app import app
from OCR.parse_register_entry_v2 import parse_register_entry

@pytest.fixture
def mock_ocr_result():
    """Returns a sample OCR result for testing purposes."""
    return {'supplier_name': 'Test Supplier', 'supplier_name_matched': 'Test Supplier Ltd', 'party_name': 'Test Party', 'party_name_matched': 'Test Party Inc', 'bill_number': '123', 'amount': 1000, 'date': '2024-01-29'}

@pytest.fixture
def mock_parse_register_entry(monkeypatch, mock_ocr_result):
    """Mocks the register entry parsing function to return a predefined OCR result."""

    def mock_parse(*args, **kwargs):
        """Mocks the parsing function to return a sample OCR result, adding a queue entry ID if in queue mode."""
        result = mock_ocr_result.copy()
        if kwargs.get('queue_mode'):
            result['queue_entry_id'] = 'test_queue_id'
        return result
    monkeypatch.setattr('OCR.parse_register_entry', mock_parse)

@pytest.fixture
def mock_ocr_queue(monkeypatch):
    """Mocks the OCR queue to simulate an empty queue for testing."""

    class MockOCRQueue:

        def get_next_entry(self):
            """Returns the next OCR queue entry; simulated as None for testing."""
            return None

        def get_status(self):
            """Returns a simulated OCR queue status dictionary for testing."""
            return {'total_pending': 0, 'total_processed': 0}

        def mark_complete(self, entry_id):
            """Marks an OCR queue entry as complete; no action in test mode."""
            pass
    monkeypatch.setattr('app.ocr_queue', MockOCRQueue())

@pytest.fixture
def client():
    """Creates and yields a Flask test client for endpoint testing."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_image_data():
    """Generates a base64-encoded string representing test image data."""
    return base64.b64encode(b'test image data').decode('utf-8')

@pytest.fixture
def sample_ocr_result():
    """Returns a sample OCR result dictionary for testing."""
    return {'supplier_name': 'Test Supplier', 'supplier_name_matched': 'Test Supplier Ltd', 'party_name': 'Test Party', 'party_name_matched': 'Test Party Inc', 'bill_number': '123', 'amount': 1000, 'date': '2024-01-29'}

def test_parse_register_entry_with_queue(client, mock_parse_register_entry):
    """Test parsing register entry with queue mode enabled."""
    image_data = io.BytesIO(b'test image data')
    data = {'image': (image_data, 'test.jpg'), 'queue_mode': 'true'}
    response = client.post('/api/parse_register_entry', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'queue_entry_id' in result

def test_parse_register_entry_without_queue(client, mock_parse_register_entry):
    """Test parsing register entry without queue mode."""
    image_data = io.BytesIO(b'test image data')
    data = {'image': (image_data, 'test.jpg'), 'queue_mode': 'false'}
    response = client.post('/api/parse_register_entry', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'queue_entry_id' not in result

def test_get_next_ocr_entry_empty(client, mock_ocr_queue):
    """Test getting next OCR entry when queue is empty."""
    response = client.get('/api/get_next_ocr_entry')
    assert response.status_code == 404
    result = json.loads(response.data)
    assert result['status'] == 'empty'
    assert 'No pending entries' in result['message']

def test_mark_ocr_complete_missing_id(client):
    """Test marking OCR entry as complete without entry ID."""
    response = client.post('/api/mark_ocr_complete', json={})
    assert response.status_code == 400
    result = json.loads(response.data)
    assert result['status'] == 'error'
    assert 'Entry ID required' in result['message']

def test_queue_status(client):
    """Test getting queue status."""
    response = client.get('/api/queue_status')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'total_pending' in result
    assert 'total_processed' in result
    assert isinstance(result['total_pending'], int)
    assert isinstance(result['total_processed'], int)

def test_complete_queue_workflow(client, mock_parse_register_entry):
    """Test complete OCR queue workflow."""
    image_data = io.BytesIO(b'test image data')
    data = {'image': (image_data, 'test.jpg'), 'queue_mode': 'true'}
    response = client.post('/api/parse_register_entry', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    parsed_result = json.loads(response.data)
    assert 'queue_entry_id' in parsed_result
    entry_id = parsed_result['queue_entry_id']
    assert entry_id == 'test_queue_id'
    response = client.get('/api/queue_status')
    result = json.loads(response.data)
    assert result['total_pending'] >= 0
    response = client.get('/api/get_next_ocr_entry')
    if response.status_code == 404:
        result = json.loads(response.data)
        assert result['status'] == 'empty'
        assert 'No pending entries' in result['message']
    else:
        assert response.status_code == 200
        entry = json.loads(response.data)
        assert 'id' in entry
        assert 'ocr_data' in entry
    response = client.post('/api/mark_ocr_complete', json={'entry_id': entry_id})
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['status'] == 'okay'

def test_parse_register_entry_no_image(client):
    """Test parsing register entry without providing an image."""
    response = client.post('/api/parse_register_entry')
    assert response.status_code == 400
    result = json.loads(response.data)
    assert result['status'] == 'error'
    assert 'No image provided' in result['message']

def test_mark_ocr_complete_invalid_id(client):
    """Test marking OCR entry as complete with invalid ID."""
    response = client.post('/api/mark_ocr_complete', json={'entry_id': 'invalid_id'})
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['status'] == 'okay'