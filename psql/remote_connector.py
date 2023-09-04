import requests
from dotenv import load_dotenv

load_dotenv()
import os

REMOTE_IP = os.getenv("REMOTE_IP")
REMOTE_PORT = os.getenv("REMOTE_PORT")
SERVER_URL = f"http://{REMOTE_IP}:{REMOTE_PORT}"

# Function to execute a remote query on the Flask server
def execute_remote_query(query, server_url=SERVER_URL):
    """
    Sends a POST request to the remote Flask server to execute a query.

    Parameters:
    - query (str): The SQL query to be executed.
    - server_url (str): The URL of the Flask server. Defaults to "http://{REMOTE_IP}:{REMOTE_PORT}".

    Returns:
    - dict: The result of the query.
    """
    
    # Endpoint for the execute_query route
    endpoint = f"{server_url}/execute_query"
    
    # Data to be sent in the POST request
    data = {
        "query": query
    }
    
    # Sending the POST request
    response = requests.post(endpoint, json=data)
    
    # Return the result as a dictionary
    return response.json()
