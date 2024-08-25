import base64
import requests
import json
import os
import dotenv
import sys
sys.path.append('../')

from Exceptions import DataError
dotenv.load_dotenv()



def _parse_response(response):
    sample_data ={
                "supplier_name": "SAI TEX FAB",
                "party_name": "SAMUNDER SAREE CENTRE",
                "date": "18/04/2023",
                "bill_number": 107,
                "amount": 69764
                }
    return sample_data
    try:
        # Ensure response is a valid JSON object
        response = response.json()

        # Check for the presence of 'choices' key
        if 'choices' not in response or not response['choices']:
            raise ValueError("Response does not contain 'choices' or it's empty.")

        # Check for 'message' and 'content' in the first choice
        if 'message' not in response['choices'][0] or 'content' not in response['choices'][0]['message']:
            raise ValueError("Response does not contain 'message' or 'content'.")

        json_response = response['choices'][0]['message']['content']

        # Attempt to parse the JSON content
        if json_response:
            return json.loads(json_response)

        else:
            raise ValueError("The 'content' field is empty.")

    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error parsing response: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    
# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def parse_register_entry(encoded_image):
    # Prompt 
    prompt = "Extract the sender/receiver name, total amount, date, and bill number (invoice number) from the invoice image and return them in the following JSON format: \
            {\"supplier_name\": \"string\", \"party_name\": \"string\", \"date\": \"DD/MM/YYYY\", \"bill_number\": \"integer or string\", \"amount\": \"integer\"}."

    # Getting the base64 string
    base64_image = encoded_image
    
  
    # OpenAI API Key
    # api_key = os.environ.get("OPENAI_API_KEY")

    # headers = {
    # "Content-Type": "application/json",
    # "Authorization": f"Bearer {api_key}"
    # }

    # payload = {
    # "model": "gpt-4o-mini",
    # "response_format": { "type": "json_object" },
    # "messages": [
    #     {
    #     "role": "user",
    #     "content": [
    #         {
    #         "type": "text",
    #         "text": prompt
    #         },
    #         {
    #         "type": "image_url",
    #         "image_url": {
    #             "url": f"data:image/jpeg;base64,{base64_image}"
    #         }
    #         }
    #     ]
    #     }
    # ],
    # "max_tokens": 300
    # }

    # response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # register_entry_data = _parse_response(response)

    return _parse_response(None)