import os
import json
import base64
import pytest
from datetime import datetime, timedelta
from OCR.ocr_queue import OCRQueue

@pytest.fixture
def queue_dir(tmp_path):
    """Returns the directory path for the OCR queue based on a temporary path."""
    return str(tmp_path / 'test_queue')

@pytest.fixture
def ocr_queue(queue_dir):
    """Initializes and returns an OCRQueue instance using the specified directory."""
    return OCRQueue(queue_dir)

@pytest.fixture
def sample_image_data():
    """Generates and returns base64-encoded test image data."""
    return base64.b64encode(b'test image data').decode()

@pytest.fixture
def sample_entry(sample_image_data):
    """Creates a sample OCR queue entry using provided test image data."""
    return {'image': sample_image_data, 'ocr_data': {'supplier_name': 'Test Supplier', 'supplier_name_matched': 'Test Supplier Ltd', 'party_name': 'Test Party', 'party_name_matched': 'Test Party Inc', 'bill_number': '123', 'amount': 1000, 'date': '2024-01-29'}}

def test_queue_initialization(ocr_queue, queue_dir):
    """Test queue initialization and directory creation."""
    assert os.path.exists(queue_dir)
    assert os.path.exists(os.path.join(queue_dir, 'images'))
    assert os.path.exists(os.path.join(queue_dir, 'queue.json'))
    with open(os.path.join(queue_dir, 'queue.json')) as f:
        data = json.load(f)
    assert 'entries' in data
    assert 'stats' in data
    assert data['stats']['total_pending'] == 0
    assert data['stats']['total_processed'] == 0

def test_add_entries(ocr_queue, sample_entry, queue_dir):
    """Test adding entries to queue."""
    entry_ids = ocr_queue.add_entries([sample_entry])
    assert len(entry_ids) == 1
    image_files = os.listdir(os.path.join(queue_dir, 'images'))
    assert len(image_files) == 1
    assert image_files[0].endswith('.jpg')
    stats = ocr_queue.get_status()
    assert stats['total_pending'] == 1
    assert stats['total_processed'] == 0

def test_get_next_entry(ocr_queue, sample_entry):
    """Test retrieving next pending entry."""
    entry_ids = ocr_queue.add_entries([sample_entry])
    entry = ocr_queue.get_next_entry()
    assert entry is not None
    assert entry['status'] == 'pending'
    assert entry['ocr_data'] == sample_entry['ocr_data']
    assert 'image' in entry
    assert entry['id'] == entry_ids[0]

def test_mark_complete(ocr_queue, sample_entry, queue_dir):
    """Test marking entries as complete."""
    entry_ids = ocr_queue.add_entries([sample_entry])
    image_files = os.listdir(os.path.join(queue_dir, 'images'))
    assert len(image_files) == 1
    ocr_queue.mark_complete(entry_ids[0])
    image_files = os.listdir(os.path.join(queue_dir, 'images'))
    assert len(image_files) == 0
    stats = ocr_queue.get_status()
    assert stats['total_pending'] == 0
    assert stats['total_processed'] == 1

def test_clear_processed(ocr_queue, sample_entry):
    """Test clearing old processed entries."""
    entry_ids = ocr_queue.add_entries([sample_entry])
    ocr_queue.mark_complete(entry_ids[0])
    old_time = (datetime.now() - timedelta(days=31)).isoformat()
    for entry in ocr_queue.queue['entries']:
        if entry['id'] == entry_ids[0]:
            entry['processed_time'] = old_time
            break
    with open(ocr_queue.queue_file) as f:
        data = json.load(f)
    data['entries'][0]['processed_time'] = old_time
    with open(ocr_queue.queue_file, 'w') as f:
        json.dump(data, f)
    ocr_queue.clear_processed(days_old=30)
    stats = ocr_queue.get_status()
    assert stats['total_pending'] == 0
    assert stats['total_processed'] == 0

def test_multiple_entries(ocr_queue, sample_entry):
    """Test handling multiple entries."""
    entries = [sample_entry, {**sample_entry, 'ocr_data': {**sample_entry['ocr_data'], 'bill_number': '124'}}, {**sample_entry, 'ocr_data': {**sample_entry['ocr_data'], 'bill_number': '125'}}]
    entry_ids = ocr_queue.add_entries(entries)
    assert len(entry_ids) == 3
    stats = ocr_queue.get_status()
    assert stats['total_pending'] == 3
    ocr_queue.mark_complete(entry_ids[0])
    ocr_queue.mark_complete(entry_ids[1])
    stats = ocr_queue.get_status()
    assert stats['total_pending'] == 1
    assert stats['total_processed'] == 2
    next_entry = ocr_queue.get_next_entry()
    assert next_entry['id'] == entry_ids[2]

def test_empty_queue(ocr_queue):
    """Test behavior with empty queue."""
    assert ocr_queue.get_next_entry() is None
    stats = ocr_queue.get_status()
    assert stats['total_pending'] == 0
    assert stats['total_processed'] == 0

def test_persistence(queue_dir, sample_entry):
    """Test queue persistence between instances."""
    queue1 = OCRQueue(queue_dir)
    entry_ids = queue1.add_entries([sample_entry])
    queue2 = OCRQueue(queue_dir)
    entry = queue2.get_next_entry()
    assert entry is not None
    assert entry['id'] == entry_ids[0]
    assert entry['ocr_data'] == sample_entry['ocr_data']
    assert 'image' in entry