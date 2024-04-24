import json
import os

from db_client import MariaDBClient
from spreadsheet_client import GoogleSheetsReader
from collections import OrderedDict


APP_PATH = f"{os.getenv('HOME')}/Github/parfumvault/docker-compose/app"
SPREADSHEET_CREDENTIALS_FILE = f"{APP_PATH}/credentials/spreadsheet_credentials.json"
DB_CREDENTIALS_FILE = f"{APP_PATH}/credentials/db_credentials.json"
MATERIALS_FILE = f"{APP_PATH}/artifacts/materials.json"


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


def read_spreadsheet_materials(fetch_remote):
    reader = GoogleSheetsReader(SPREADSHEET_CREDENTIALS_FILE)

    if fetch_remote:
        sheet_ingredients = reader.read_data(
            "Perfume Personal Worksheet", "Materials", "B3:AB307")
        with open(MATERIALS_FILE, "w") as f:
            json.dump(sheet_ingredients, f)
    else:
        with open(MATERIALS_FILE, "r") as f:
            sheet_ingredients = json.load(f)

    return sheet_ingredients


def import_spreadsheet_materials(fetch_from_remote=False,
                                 import_ingCategory=False, import_ingredients=False, import_ingExtraProperties=False
                                 ):
    sheet_ingredients = read_spreadsheet_materials(fetch_from_remote)

    # `type` here is not the same as 'sheet_cols' type. Type here is 'AC' for all ingredients
    db_ingredients_cols = ['name', 'type', 'profile', 'notes', 'odor', 'strength', 'category',
                           'tenacity', 'rdi', 'cas', 'molecularWeight']

    db_ingCategory_cols = ['type']

    # `rdi` is sheet sometimes contain extra string, we should split on the first space
    # `tags` are comma separated
    # `category` is a int that refers to a int in the `ingcategory` table, which is a table with `id`, `name` where `name` refers to `type` in 'sheet_cols'
    sheet_cols = ['class', 'name', 'type', 'type2', 'profile', 'profile2', 'fullProfile', 'notes',
                  'odor', 'ifraRestriction', 'dilutionPercentiles', 'availableDilutions', 'storeInFridge',
                  'strength', 'tenacityOnPaper', 'tenacity', 'rdi', 'diluteNotes', 'cas', 'casEU',
                  'molecularWeight', 'purchaseLink', 'moreInfo1', 'moreInfo2', 'moreInfo3',
                  'addedByMe', 'tags']

    sheet_results = create_dict_list(sheet_cols, sheet_ingredients)

    with open(DB_CREDENTIALS_FILE) as f:
        db_client = MariaDBClient(**json.load(f))

    if import_ingCategory:
        # Importing `ingCategory`
        ingCategory_results = filter_dict_list_by_keys(
            sheet_results, db_ingCategory_cols)
        import_db_ingCategory_data = transform_entry_in_dict_list(
            ingCategory_results, entry_map={
                'name': 'type',
            },
            delete_entries=['type'],
        )
        db_client.upsert(table_name="ingCategory",
                         data=import_db_ingCategory_data)

    if import_ingredients:
        # Getting `ingCategory` ids
        db_ingCategory_results = db_client.execute(
            'SELECT id,name FROM pvault.ingCategory')
        db_ingCategory_map = {}
        for db_ingCategory_result in db_ingCategory_results:
            db_ingCategory_map[db_ingCategory_result['name']
                               ] = db_ingCategory_result['id']

        # Importing `ingredients`
        ingredients_results = filter_dict_list_by_keys(
            sheet_results, db_ingredients_cols)
        import_db_ingredients_data = transform_entry_in_dict_list(
            ingredients_results,
            entry_map=OrderedDict([
                ('category', 'type'),
                ('type', 'name'),
            ]),
            transform_functions={
                'type': lambda type: 'EO' if 'EO' in type else 'AC',
                'profile': lambda profile: 'Heart' if profile == 'Middle' else profile,
                'strength': lambda strength: strength.capitalize(),
                'category': lambda category: db_ingCategory_map[category],
                'rdi': lambda rdi: int(rdi.split(' ')[0]) if rdi != '' else 0,
                'purity': '100',
            },
        )
        db_client.upsert(table_name="ingredients",
                         data=import_db_ingredients_data)

    if import_ingExtraProperties:
        # Getting `ingredients` ids
        db_ingredients_results = db_client.execute(
            'SELECT id,name FROM pvault.ingredients')
        db_ingredients_map = {}
        for db_ingredients_result in db_ingredients_results:
            db_ingredients_map[db_ingredients_result['name']
                               ] = db_ingredients_result['id']

        # Import `ingExtraProperties`
        db_ingExtraProperties_cols = ['name'] + [
            item for item in sheet_cols if item not in db_ingredients_cols]

        ingExtraProperties_results = filter_dict_list_by_keys(
            sheet_results, db_ingExtraProperties_cols)
        import_db_ingExtraProperties_data = transform_entry_in_dict_list(
            ingExtraProperties_results,
            entry_map={
                'ingredient_id': 'name',
                'ingredient_name': 'name',
            },
            transform_functions={
                'ingredient_id': lambda name: db_ingredients_map[name],
            },
            delete_entries=['name'],
        )

        db_client.upsert(table_name="ingExtraProperties",
                         data=import_db_ingExtraProperties_data)


if __name__ == "__main__":
    import_spreadsheet_materials(
        fetch_from_remote=False,
        import_ingCategory=False,
        import_ingredients=True,
        import_ingExtraProperties=False,
    )
