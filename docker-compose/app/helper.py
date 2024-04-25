

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