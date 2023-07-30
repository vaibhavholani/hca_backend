import json

class DataError(Exception):
    def __init__(self, error_dict):
        if (type(error_dict) == str):
            error_dict = {"status": "error", "message": "error_dict"}
        self.error_dict = error_dict
        super().__init__("an error has occurred")
    
    def dict(self):
        return self.error_dict