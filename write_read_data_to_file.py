import os
import json


def write_data_to_file(file_name: str, data: dict):
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r') as file:
                existing_data = json.load(file)
        except json.JSONDecodeError:
            # If file is empty, initialize existing_data as an empty dictionary
            existing_data = {}
    else:
        # If file doesn't exist, initialize existing_data as an empty dictionary
        existing_data = {}

    existing_data.update(data)

    with open(file_name, 'w') as file:
        json.dump(existing_data, file)

    return existing_data

def read_data_from_file(file_name: str):
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding="utf8") as file:
                existing_data = json.load(file)
        except json.JSONDecodeError:
            # If file is empty, initialize existing_data as an empty dictionary
            existing_data = {}
    else:
        # If file doesn't exist, initialize existing_data as an empty dictionary
        existing_data = {}
        with open(file_name, 'w') as file:
            json.dump(existing_data, file)
    
    return existing_data


print(read_data_from_file('test.json'))