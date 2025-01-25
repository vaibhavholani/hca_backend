import pytest
import base64
import os
from pathlib import Path

from OCR.parse_register_entry_v2 import InvoiceParser, parse_register_entry

class TestOCR:
    @pytest.fixture
    def invoice_parser(self):
        return InvoiceParser()

    def test_invoice_parser_initialization(self, invoice_parser):
        """Test that the invoice parser initializes correctly."""
        assert invoice_parser.llm is not None
        assert invoice_parser.output_parser is not None
        assert invoice_parser.prompt is not None

    def test_encode_image(self, invoice_parser, tmp_path):
        """Test image encoding function."""
        # Create a dummy image file
        test_file = tmp_path / "test_image.jpg"
        test_file.write_bytes(b"dummy image content")
        
        # Test encoding
        encoded = invoice_parser.encode_image(str(test_file))
        assert isinstance(encoded, str)
        assert base64.b64decode(encoded)  # Verify it's valid base64

    @pytest.mark.integration
    def test_parse_invoice(self, invoice_parser, tmp_path):
        """
        Integration test for invoice parsing.
        Note: This test requires a valid OpenAI API key and will make an API call.
        """
        # Skip if no API key
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OpenAI API key not found")

        # Create a dummy image
        test_file = tmp_path / "test_image.jpg"
        test_file.write_bytes(b"dummy image content")
        encoded_image = invoice_parser.encode_image(str(test_file))

        # Test parsing
        try:
            result = invoice_parser.parse_invoice(encoded_image)
            assert isinstance(result, dict)
            assert "supplier_name" in result
            assert "party_name" in result
            assert "date" in result
            assert "bill_number" in result
            assert "amount" in result
        except Exception as e:
            pytest.fail(f"Parse invoice failed: {str(e)}")

    def test_parse_register_entry_function(self, tmp_path):
        """Test the main parse_register_entry function."""
        # Skip if no API key
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OpenAI API key not found")

        # Create a dummy image
        test_file = tmp_path / "test_image.jpg"
        test_file.write_bytes(b"dummy image content")
        
        with open(test_file, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        try:
            result = parse_register_entry(encoded_image)
            assert isinstance(result, dict)
            assert all(key in result for key in ["supplier_name", "party_name", "date", "bill_number", "amount"])
        except Exception as e:
            pytest.fail(f"Parse register entry failed: {str(e)}")
