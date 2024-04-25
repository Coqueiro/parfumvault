import json
import os

from db_client import MariaDBClient
from spreadsheet_client import GoogleSheetsReader
from collections import OrderedDict

from helper import transform_entry_in_dict_list, create_dict_list, filter_dict_list_by_keys


APP_PATH = f"{os.getenv('HOME')}/Github/parfumvault/docker-compose/app"
SPREADSHEET_CREDENTIALS_FILE = f"{APP_PATH}/credentials/spreadsheet_credentials.json"
DB_CREDENTIALS_FILE = f"{APP_PATH}/credentials/db_credentials.json"
MATERIALS_FILE = f"{APP_PATH}/spreadsheet_cache/materials.json"


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
                'profile': lambda profile: 'Heart' if profile.capitalize() == 'Middle' else profile.capitalize(),
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
        import_ingredients=False,
        import_ingExtraProperties=False,
    )
