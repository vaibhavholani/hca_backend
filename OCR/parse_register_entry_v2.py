import base64
import os
import sys
from typing import Optional
from datetime import datetime

sys.path.append('../')

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from dotenv import load_dotenv

from Exceptions import DataError
from .name_matcher import NameMatcher

load_dotenv()

class InvoiceData(BaseModel):
    """Data model for invoice information."""
    supplier_name: str = Field(description="Name of the supplier")
    party_name: Optional[str] = Field(description="Name of the party")
    date: str = Field(description="Date in yyyy-MM-dd format")
    bill_number: str = Field(description="Bill or invoice number")
    amount: int = Field(description="Total amount")

class InvoiceParser:
    def __init__(self):
        """Initialize the invoice parser with LangChain components."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key,
            max_tokens=300,
            temperature=0
        )
        
        self.output_parser = PydanticOutputParser(pydantic_object=InvoiceData)
        self.prompt = self._create_prompt()

    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for invoice parsing."""
        template = """Extract the following information from the invoice image:
        - Supplier name (sender)
        - Party name (receiver)
        - Date (convert to yyyy-MM-dd format)
        - Bill/invoice number
        - Total amount (as integer)

        {format_instructions}

        If any field is not found, use null for party_name or appropriate empty values for other fields.
        """
        
        return ChatPromptTemplate.from_messages([
            ("system", template),
            ("human", "Process this invoice image and extract the required information.")
        ]).partial(format_instructions=self.output_parser.get_format_instructions())

    def encode_image(self, image_path: str) -> str:
        """Encode an image file to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def parse_invoice(self, encoded_image: str) -> dict:
        """Parse invoice information from a base64 encoded image."""
        try:
            # Prepare the message with image
            messages = self.prompt.format_messages()
            messages[1].content = [
                {
                    "type": "text",
                    "text": messages[1].content
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}"
                    }
                }
            ]

            # Get response from LLM
            response = self.llm.invoke(messages)
            
            # Parse and validate the response
            parsed_data = self.output_parser.parse(response.content)
            
            # Convert to dict for consistency with existing code
            return parsed_data.model_dump()

        except Exception as e:
            print(f"Error parsing invoice: {str(e)}")
            raise DataError({"status": "error", "message": f"Error parsing invoice: {str(e)}"})

def parse_register_entry(encoded_image: str) -> dict:
    """Main function to parse register entries from images."""
    try:
        # Parse invoice using OCR
        parser = InvoiceParser()
        result = parser.parse_invoice(encoded_image)
        
        # Initialize name matcher
        matcher = NameMatcher()
        
        # Match supplier name if present
        if result.get('supplier_name'):
            matched_supplier = matcher.find_match(result['supplier_name'], 'supplier')
            result['supplier_name'] = matched_supplier if matched_supplier else result['supplier_name']
        
        # Match party name if present
        if result.get('party_name'):
            matched_party = matcher.find_match(result['party_name'], 'party')
            result['party_name'] = matched_party if matched_party else result['party_name']
        
        return result
    except Exception as e:
        print(f"Error in parse_register_entry: {str(e)}")
        raise DataError({"status": "error", "message": f"Error processing invoice: {str(e)}"})

# Keep the encode_image function at module level for backward compatibility
def encode_image(image_path: str) -> str:
    """Encode an image file to base64 string."""
    parser = InvoiceParser()
    return parser.encode_image(image_path)

# Example usage:
# encoded_image = encode_image("path/to/image.jpg")
# result = parse_register_entry(encoded_image)
# print(f"Parsed and matched result: {result}")
