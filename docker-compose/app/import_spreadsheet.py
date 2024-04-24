import os
from db_client import MariaDBClient
from spreadsheet_client import GoogleSheetsReader
from apps_script_client import run_function, authorize_script_api

def db_test():
    db_client = MariaDBClient(
        host="pvaultdb.rasp",
        port=3306,
        database="pvault",
        user="pvault",
        password="pvault"
    )
    results = db_client.execute(
        "SELECT * FROM pvault.ingredients WHERE id < %s", [4])
    print(results)

    # data = {"id": 1, "name": "Alice", "score": 85}
    # db_client.upsert("scores", data, "id")
    # results = db_client.read("pvault.ingredients") #, columns=["name", "score"], where_clause="score > %s", params=[70])
    # print(results)


def spreadsheet_test():
    credentials_file = f"{os.getenv('PWD')}/docker-compose/app/spreadsheet_credentials.json"
    reader = GoogleSheetsReader(credentials_file)

    results = reader.read_data(
        "Perfume Personal Worksheet", "Formulas", "B147:G185")
    print(results)


def apps_script_test():
    script_id = "15DnFNALhMuMlEPZ70t06ACYfrYVIiJKOQkcv5rnG8GaBEn1MZfFjGT3o"
    script_url = "https://script.google.com/macros/s/AKfycbz4qF_N7bbUYY3hQgDbszm6NYAoL1bqdJ7T130U1p2wMmCKGR3tFVqpesSyAB31HOlQHQ/exec"
    function_name = "testGetFormula"
    argument = "Pineapple Gemini Base"
    credentials_file = f"{os.getenv('PWD')}/docker-compose/app/spreadsheet_credentials.json"
    credentials = authorize_script_api(credentials_file)

    result = run_function(script_url, script_id, function_name, argument, credentials)
    print(result)


if __name__ == "__main__":
    # db_test()
    # spreadsheet_test()
    # apps_script_test()
    pass
