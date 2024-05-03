import json
import os.path

def load_json_if_exists(file_path):
    """Tries to load JSON data from a file if it exists.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The loaded JSON data as a dictionary, or None if the file doesn't exist or the JSON is invalid.
    """

    if os.path.isfile(file_path):  # Check if the file exists
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON data in the {file_path.split('/')[-1]} file.")
            return None
    else:
        print(f"File {file_path.split('/')[-1]} not found.")
        return None

def merge_dictionaries(file_path, new_dictionaries, key):
    """Merges dictionaries from a file with new dictionaries, removing duplicates.

    Args:
        file_path (str): Path to the JSON file containing the original dictionaries.
        new_dictionaries (list): List of new dictionaries to merge.

    Returns:
        list: The merged list of dictionaries with duplicates removed.
    """

    try:
        # Load existing dictionaries from the file
        with open(file_path, 'r') as f:
            existing_dictionaries = json.load(f)
    except FileNotFoundError:
        existing_dictionaries = []  # Start with an empty list if the file doesn't exist

    # Create a combined list and a set to track seen key for deduplication
    combined_dictionaries = existing_dictionaries + new_dictionaries
    seen_keys = set()

    # Filter duplicates, prioritizing 'new_dictionaries'
    merged_dictionaries = []
    for dictionary in combined_dictionaries:
        key = dictionary[key]
        if key not in seen_keys:
            merged_dictionaries.append(dictionary)
            seen_keys.add(key)

    return merged_dictionaries

def create_dict_list(header, data):
    """
    Creates a list of dictionaries from a header list and a list of lists.

    Args:
        header (list): A list of strings representing the keys of the dictionaries.
        data (list): A list of lists containing the values for each dictionary.

    Returns:
        list: A list of dictionaries where each dictionary is composed of keys
              from the header and values from the data. Missing values are filled 
              with None.
    """

    dict_list = []
    for row in data:
        dict_list.append(
            dict(zip(header, row + [None] * (len(header) - len(row))))
        )
    return dict_list


def filter_dict_list_by_keys(data, intersect_keys):
    """
    Filters a list of dictionaries, keeping only keys present in the intersect_keys list.

    Args:
        data (list): A list of dictionaries.
        intersect_keys (list): A list of strings representing the desired keys.

    Returns:
        list: A list of dictionaries containing only the keys from intersect_keys.
    """

    filtered_data = []
    for item in data:
        filtered_dict = {key: item[key]
                         for key in intersect_keys if key in item}
        filtered_data.append(filtered_dict)

    return filtered_data


def transform_entry_in_dict_list(data, entry_map={}, transform_functions={}, delete_entries=[]):
    """
    Applies a transformation function to the "entry" entry of each dictionary in a list.

    Args:
        data (list): A list of dictionaries.
        transform_functions (dict(str, function)): A dictionary of entries and functions that takes a value and returns a transformed value.

    Returns:
        list: A new list of dictionaries with the "entry" entry transformed.
    """

    transformed_data = []
    for item in data:
        # Create a copy to avoid modifying the original dictionary
        transformed_dict = dict(item)
        for new_entry, entry in entry_map.items():
            transformed_dict[new_entry] = transformed_dict[entry]
        for entry, transform_function in transform_functions.items():
            if entry in transformed_dict:
                transformed_dict[entry] = transform_function(
                    transformed_dict[entry])
        for del_entry in delete_entries:
            del transformed_dict[del_entry]
        transformed_data.append(transformed_dict)
    return transformed_data
