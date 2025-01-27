import pytest
import base64
import os
from pathlib import Path
from hca_backend.OCR.parse_register_entry_v2 import parse_register_entry
from hca_backend.OCR.name_cache import NameMatchCache
from hca_backend.app import app

class TestOCRIntegration:
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def mock_cache(self, monkeypatch, temp_cache_file):
        """Create a mock cache for testing."""
        cache = NameMatchCache(temp_cache_file)
        monkeypatch.setattr('hca_backend.app.name_cache', cache)
        return cache

    @pytest.fixture
    def test_image(self, temp_cache_dir):
        """Create a copy of the test image in the temporary directory."""
        source_image = os.path.join(os.path.dirname(__file__), "test_data", "test_image.jpeg")
        test_file = os.path.join(temp_cache_dir, "test_bill.jpeg")
        with open(source_image, 'rb') as src, open(test_file, 'wb') as dst:
            dst.write(src.read())
        return test_file

    def test_ocr_with_human_correction_flow(self, client, mock_cache, test_image):
        """Test the complete flow from OCR to human correction and learning."""
        # Skip if no API key
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OpenAI API key not found")

        # Step 1: Initial OCR
        with open(test_image, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        initial_result = parse_register_entry(encoded_image)
        assert isinstance(initial_result, dict)
        
        original_supplier = initial_result.get('supplier_name')
        original_party = initial_result.get('party_name')
        assert original_supplier is not None
        assert original_party is not None

        # Step 2: Simulate human correction for supplier
        corrected_supplier = "Corrected Supplier Ltd"
        response = client.post('/update_name_mapping', json={
            'original_name': original_supplier,
            'corrected_name': corrected_supplier,
            'entity_type': 'supplier'
        })
        assert response.status_code == 200

        # Step 3: Verify cache was updated
        assert mock_cache.get(original_supplier) == corrected_supplier

        # Step 4: Process same image again
        # Commenting this
        # second_result = parse_register_entry(encoded_image)
        # assert isinstance(second_result, dict)
        
        # # Step 5: Verify the corrected name is used
        # assert second_result.get('supplier_name') == corrected_supplier

        # Step 6: Test cache stats
        stats = mock_cache.get_stats()
        assert stats['total_entries'] > 0
        assert stats['hits'] > 0

    def test_multiple_corrections_learning(self, client, mock_cache):
        """Test that system learns from multiple corrections."""
        # Initial mapping
        client.post('/update_name_mapping', json={
            'original_name': 'Test Supplier',
            'corrected_name': 'Test Supplier Limited',
            'entity_type': 'supplier'
        })

        # Similar name variations that should match
        assert mock_cache.get('Test Supplier Ltd') == 'Test Supplier Limited'
        assert mock_cache.get('Test Supplier Pvt') == 'Test Supplier Limited'

        # Different variations of the same company
        variations = [
            'Test Supplier Private Ltd',
            'Test Supplier Pvt Limited',
            'TEST SUPPLIER LTD'
        ]

        for variant in variations:
            client.post('/update_name_mapping', json={
                'original_name': variant,
                'corrected_name': 'Test Supplier Limited',
                'entity_type': 'supplier'
            })

        # Verify all variations map to the same corrected name
        for variant in variations:
            assert mock_cache.get(variant) == 'Test Supplier Limited'

        # Verify fuzzy matching works for new, similar names
        assert mock_cache.get('Test Supplier Pvt. Ltd.') == 'Test Supplier Limited'

    def test_correction_precedence(self, client, mock_cache):
        """Test that human corrections take precedence over AI predictions."""
        # Initial AI prediction (simulated)
        mock_cache.set('Original Corp', 'AI Predicted Name')
        
        # Human correction
        client.post('/update_name_mapping', json={
            'original_name': 'Original Corp',
            'corrected_name': 'Human Corrected Name',
            'entity_type': 'supplier'
        })
        
        # Verify human correction overrides AI prediction
        assert mock_cache.get('Original Corp') == 'Human Corrected Name'
        
        # Verify similar names match the human correction
        assert mock_cache.get('Original Corp Ltd') == 'Human Corrected Name'
        assert mock_cache.get('Original Corp Private') == 'Human Corrected Name'
