from supabase import create_client, Client
from dotenv import load_dotenv
import os
load_dotenv()
url: str = 'https://onlrctexmxyahbjsfprm.supabase.co'
key: str = os.getenv('SUPBASE_KEY')
supabase: Client = create_client(url, key)

def update_user_role(user_id: str, new_role: str):
    """Updates a user's role using Supabase admin functions."""
    try:
        user_response = supabase.auth.admin.get_user_by_id(user_id)
        user = user_response.user
        if not user:
            print(f'User with ID {user_id} not found.')
            return
        response = supabase.auth.admin.update_user_by_id(user_id, {'role': new_role, 'user_metadata': {'role': new_role}})
        if response.user:
            print(f'User role updated to {new_role} successfully!')
        else:
            print(f"Failed to update user role: {response.get('error').get('message')}")
    except Exception as e:
        print(f'Error occurred: {str(e)}')
update_user_role('1a083b6c-f2fd-4581-bbde-9aaebfff3682', 'developer')

def check_user_role(user_id: str):
    """Retrieves and prints the user's role using Supabase admin functions."""
    try:
        user_response = supabase.auth.admin.get_user_by_id(user_id)
        user = user_response.user
        if user:
            role = user.role
            print(f'User role: {role}')
        else:
            print(f'User with ID {user_id} not found.')
    except Exception as e:
        print(f'Error occurred: {str(e)}')