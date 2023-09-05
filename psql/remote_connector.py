import requests
from dotenv import load_dotenv
import os
load_dotenv()

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
    from API_Database import insert_remote_query_log

    # Endpoint for the execute_query route
    endpoint = f"{server_url}/execute_query"

    # Data to be sent in the POST request
    data = {
        "query": query
    }

    try:
        # Sending the POST request
        response = requests.post(endpoint, json=data)
        response.raise_for_status()  # Check if the request was successful

        # Extract query_status and message if they exist
        response_data = response.json()
        query_status = response_data.get("status", "")
        message = response_data.get("message", "")

        # Log the query execution in the database
        return insert_remote_query_log(query, response.status_code, query_status, message)

    except requests.ConnectionError:
        print("Error: Unable to connect to the server.")
        insert_remote_query_log(
            query, 999, "ConnectionError", "Unable to connect to the server.")
        return {"status": "error", "message": "Unable to connect to the server."}
    except requests.HTTPError:
        error_msg = f"HTTP Error {response.status_code}: {response.text}"
        insert_remote_query_log(
            query, response.status_code, "HTTPError", error_msg)
        return {"status": "error", "message": error_msg}
    except requests.RequestException:
        print("Error occurred while making the request.")
        insert_remote_query_log(
            query, 999, "RequestException", "Error occurred while making the request.")
        return {"status": "error", "message": "Error occurred while making the request."}
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        insert_remote_query_log(query, 999, "Exception", error_msg)
        return {"status": "error", "message": error_msg}
