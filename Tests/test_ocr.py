import pytest
import base64
import os
from pathlib import Path
from hca_backend.OCR.parse_register_entry_v2 import InvoiceParser, parse_register_entry

class TestOCR:

    @pytest.fixture
    def invoice_parser(self):
        """Initializes and returns an InvoiceParser instance for OCR functionality testing."""
        return InvoiceParser()

    def test_invoice_parser_initialization(self, invoice_parser):
        """Test that the invoice parser initializes correctly."""
        assert invoice_parser.llm is not None
        assert invoice_parser.output_parser is not None
        assert invoice_parser.prompt is not None

    def test_encode_image(self, invoice_parser, tmp_path):
        """Test image encoding function."""
        test_file = tmp_path / 'test_image.jpg'
        test_file.write_bytes(b'dummy image content')
        encoded = invoice_parser.encode_image(str(test_file))
        assert isinstance(encoded, str)
        assert base64.b64decode(encoded)

    def test_bill_number_processing(self, invoice_parser):
        """Test the AI-powered bill number processing with various formats."""
        if not os.getenv('OPENAI_API_KEY'):
            pytest.skip('OpenAI API key not found')
        test_cases = [('RF/123', 'Rachit Fashion', '123'), ('ABC-456', 'ABC Textiles', '456'), ('123/23-24', 'Some Supplier', '123'), ('2024/456', 'Some Supplier', '456'), ('456/2024', 'Some Supplier', '456'), ('BOM/RF/789/23-24', 'Rachit Fashion', '789'), ('RF_BOM_101_2024', 'Rachit Fashion', '101'), ('12345', 'Any Supplier', '12345'), ('INV-2024-001', 'Some Supplier', '001'), ('PO/2024/Q4/789', 'Some Supplier', '789'), ('VK/101', 'V.K. Fabrics', '101'), ('RACHIT/2024/202', 'Rachit Fashion', '202')]
        for (input_number, supplier_name, expected) in test_cases:
            try:
                result = invoice_parser.process_bill_number(input_number, supplier_name)
                assert result == expected, f"Failed for input '{input_number}' (supplier: {supplier_name}): expected '{expected}', got '{result}'"
            except Exception as e:
                pytest.fail(f"Bill number processing failed for '{input_number}' (supplier: {supplier_name}): {str(e)}")