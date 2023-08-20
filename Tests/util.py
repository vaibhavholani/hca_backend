from __future__ import annotations
from typing import Dict, Union, List
from Entities import RegisterEntry, MemoEntry, OrderForm
from Individual import Supplier, Party
from Exceptions import DataError
# Import stack data structure
from collections import deque

def check_status_and_return_class(status: Dict) -> Union[Supplier, Party, RegisterEntry, MemoEntry, OrderForm]:
    if status["status"] == "okay":
        return status["class"]
    else:
        raise DataError(status)

# Function to find differences between two dictionaries
def print_dict_diff(dict1, dict2, path=""):
    """
    Compare two dictionaries and print differences.
    """
    # If both values are dictionaries, recursively compare them
    if isinstance(dict1, dict) and isinstance(dict2, dict):
        for key in dict1:
            if key in dict2:
                print_dict_diff(dict1[key], dict2[key], path=path + f"[{key}]")
            else:
                print(f"Key {path}[{key}] present in dict1, missing in dict2.")
                print(f"Value in dict1 = {dict1[key]}")
                print("Value in dict2 = None")
        for key in dict2:
            if key not in dict1:
                print(f"Key {path}[{key}] missing in dict1, present in dict2.")
                print("Value in dict1 = None")
                print(f"Value in dict2 = {dict2[key]}")
    # If both values are lists, compare each element
    elif isinstance(dict1, list) and isinstance(dict2, list):
        min_len = min(len(dict1), len(dict2))
        for index in range(min_len):
            print_dict_diff(dict1[index], dict2[index], path=path + f"[{index}]")
        if len(dict1) > min_len:
            for index in range(min_len, len(dict1)):
                print(f"Index {path}[{index}] present in list1, missing in list2.")
                print(f"Value in list1 = {dict1[index]}")
                print("Value in list2 = None")
        elif len(dict2) > min_len:
            for index in range(min_len, len(dict2)):
                print(f"Index {path}[{index}] missing in list1, present in list2.")
                print("Value in list1 = None")
                print(f"Value in list2 = {dict2[index]}")
    # If values are of different types or differ
    else:
        if dict1 != dict2:
            print(f"Difference at {path}:")
            print(f"Value in dict1 = {dict1}")
            print(f"Value in dict2 = {dict2}")

def cleanup(cls: List[Union[Supplier, Party, RegisterEntry, MemoEntry]]):

    while len(cls) > 0:
        obj = cls.pop()
        try:
            obj.delete()
            print(f"Deleted {obj.__class__.__name__}")
        except Exception as e:
            print(f"Exception while deleting {obj.__class__.__name__} with id {obj.get_id()}")
            print(e)
            print("Continuing with cleanup")