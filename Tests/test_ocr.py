import pytest
import base64
import os
from pathlib import Path

from hca_backend.OCR.parse_register_entry_v2 import InvoiceParser, parse_register_entry

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

    # @pytest.mark.integration
    # def test_parse_invoice(self, invoice_parser, tmp_path):
    #     """
    #     Integration test for invoice parsing.
    #     Note: This test requires a valid OpenAI API key and will make an API call.
    #     """
    #     # Skip if no API key
    #     if not os.getenv("OPENAI_API_KEY"):
    #         pytest.skip("OpenAI API key not found")

    #     # Create a dummy image
    #     test_file = tmp_path / "test_image.jpg"
    #     test_file.write_bytes(b"dummy image content")
    #     encoded_image = invoice_parser.encode_image(str(test_file))

    #     # Test parsing
    #     try:
    #         result = invoice_parser.parse_invoice(encoded_image)
    #         assert isinstance(result, dict)
    #         assert "supplier_name" in result
    #         assert "party_name" in result
    #         assert "date" in result
    #         assert "bill_number" in result
    #         assert "amount" in result
    #     except Exception as e:
    #         pytest.fail(f"Parse invoice failed: {str(e)}")

    # def test_parse_register_entry_function(self, tmp_path):
    #     """Test the main parse_register_entry function."""
    #     # Skip if no API key
    #     if not os.getenv("OPENAI_API_KEY"):
    #         pytest.skip("OpenAI API key not found")

    #     # Create a dummy image
    #     test_file = tmp_path / "test_image.jpg"
    #     test_file.write_bytes(b"dummy image content")
        
    #     with open(test_file, "rb") as image_file:
    #         encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    #     try:
    #         result = parse_register_entry(encoded_image)
    #         assert isinstance(result, dict)
    #         assert all(key in result for key in ["supplier_name", "party_name", "date", "bill_number", "amount"])
    #     except Exception as e:
    #         pytest.fail(f"Parse register entry failed: {str(e)}")

    def test_bill_number_processing(self, invoice_parser):
        """Test the AI-powered bill number processing with various formats."""
        # Skip if no API key
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OpenAI API key not found")

        test_cases = [
            # Company initials matching supplier name
            ("RF/123", "Rachit Fashion", "123"),  # Company initials with slash
            ("ABC-456", "ABC Textiles", "456"),  # Company initials with hyphen
            
            # Year formats (using current year)
            ("123/23-24", "Some Supplier", "123"),  # Bill number with financial year
            ("2024/456", "Some Supplier", "456"),  # Current year prefix
            ("456/2024", "Some Supplier", "456"),  # Current year suffix
            
            # Complex formats with supplier context
            ("BOM/RF/789/23-24", "Rachit Fashion", "789"),  # Branch/Company/Number/Year
            ("RF_BOM_101_2024", "Rachit Fashion", "101"),  # Underscores with multiple parts
            
            # Pure numeric (should remain unchanged)
            ("12345", "Any Supplier", "12345"),
            
            # Edge cases with context
            ("INV-2024-001", "Some Supplier", "001"),  # Invoice prefix with year and padding
            ("PO/2024/Q4/789", "Some Supplier", "789"),  # Purchase order with multiple segments
            
            # Supplier name variations
            ("VK/101", "V.K. Fabrics", "101"),  # Abbreviated supplier name
            ("RACHIT/2024/202", "Rachit Fashion", "202")  # Full name in bill number
        ]

        for input_number, supplier_name, expected in test_cases:
            try:
                result = invoice_parser.process_bill_number(input_number, supplier_name)
                assert result == expected, f"Failed for input '{input_number}' (supplier: {supplier_name}): expected '{expected}', got '{result}'"
            except Exception as e:
                pytest.fail(f"Bill number processing failed for '{input_number}' (supplier: {supplier_name}): {str(e)}")
