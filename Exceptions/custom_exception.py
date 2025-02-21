import json

class DataError(Exception):

    def __init__(self, error_dict):
        """Initializes a custom exception using an error dictionary; converts string errors to a dictionary if needed."""
        if type(error_dict) == str:
            error_dict = {'status': 'error', 'message': error_dict}
        self.error_dict = error_dict
        super().__init__('an error has occurred')

    def dict(self):
        """Returns the error dictionary associated with this exception."""
        return self.error_dict