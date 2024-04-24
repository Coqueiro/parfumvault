import json
import os

from apps_script_client import authorize_script_api, run_function
from db_client import MariaDBClient
from spreadsheet_client import GoogleSheetsReader


APP_PATH = f"{os.getenv('HOME')}/Github/parfumvault/docker-compose/app"
SPREADSHEET_CREDENTIALS_FILE = f"{APP_PATH}/spreadsheet_credentials.json"
DB_CREDENTIALS_FILE = f"{APP_PATH}/db_credentials.json"
MATERIALS_FILE = f"{APP_PATH}/materials.json"


def db_test():
    with open(DB_CREDENTIALS_FILE) as f:
        db_client = MariaDBClient(**json.load(f))

    # results = db_client.read("pvault.ingredients") #, columns=["name", "score"], where_clause="id < %s", params=[4])
    results = db_client.execute(
        "SELECT * FROM pvault.ingredients WHERE id < %s", [4])
    print(results)



def db_upsert_test():
    with open(DB_CREDENTIALS_FILE) as f:
        db_client = MariaDBClient(**json.load(f))

    data = [
        {"name": "Hydroxycitronellal", "type": "AC"},
        {"name": "Vanillin Crystals", "type": "AC"},
    ]
    db_client.upsert(table_name="ingredients", data=data)


def read_spreadsheet_materials(fetch_remote=False):
    reader = GoogleSheetsReader(SPREADSHEET_CREDENTIALS_FILE)

    if fetch_remote:
        results = reader.read_data(
            "Perfume Personal Worksheet", "Materials", "C3:AB307")
        with open(MATERIALS_FILE, "w") as f:
            json.dump(results, f)
    else:
        print(MATERIALS_FILE)
        with open(MATERIALS_FILE, "r") as f:
            results = json.load(f)
    print(results)


def apps_script_test():
    script_url = "https://script.google.com/macros/s/AKfycbz4qF_N7bbUYY3hQgDbszm6NYAoL1bqdJ7T130U1p2wMmCKGR3tFVqpesSyAB31HOlQHQ/exec"
    script_id = "15DnFNALhMuMlEPZ70t06ACYfrYVIiJKOQkcv5rnG8GaBEn1MZfFjGT3o"
    function_name = "testGetFormula"
    argument = "Pineapple Gemini Base"

    credentials = authorize_script_api(SPREADSHEET_CREDENTIALS_FILE)

    result = run_function(script_url, script_id,
                          function_name, argument, credentials)
    print(result)


if __name__ == "__main__":
    # db_test()
    # db_upsert_test()
    read_spreadsheet_materials()
    # apps_script_test()
    pass
