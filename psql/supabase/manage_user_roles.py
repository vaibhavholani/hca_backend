from supabase import create_client, Client
from dotenv import load_dotenv
import os

# LOAD ENVIRONMENT VARIABLES
load_dotenv()

url: str = "https://onlrctexmxyahbjsfprm.supabase.co"
key: str = os.getenv("SUPBASE_KEY") # Service Role Key
supabase: Client = create_client(url, key)

def update_user_role(user_id: str, new_role: str):
    try:
        # Fetch the user data
        user_response = supabase.auth.admin.get_user_by_id(user_id)
        user = user_response.user
        
        if not user:
            print(f"User with ID {user_id} not found.")
            return
        
        # Update the user's metadata with the new role
        response = supabase.auth.admin.update_user_by_id(user_id, {
            'role': new_role,
            'user_metadata': {
                'role': new_role
            }
        })


        if response.user:
            print(f"User role updated to {new_role} successfully!")
        else:
            print(f"Failed to update user role: {response.get('error').get('message')}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

# Example usage:
update_user_role("1a083b6c-f2fd-4581-bbde-9aaebfff3682", "developer")

def check_user_role(user_id: str):
    try:
        user_response = supabase.auth.admin.get_user_by_id(user_id)
        
        user = user_response.user
        if user:
            role = user.role
            print(f"User role: {role}")
        else:
            print(f"User with ID {user_id} not found.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

# Example usage:
# check_user_role("1a083b6c-f2fd-4581-bbde-9aaebfff3682")






