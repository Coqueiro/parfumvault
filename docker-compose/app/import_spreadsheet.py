import os
from db_client import MariaDBClient
from spreadsheet_client import GoogleSheetsReader
from apps_script_client import run_apps_script

# **How to use the class**
# 1. Install MariaDB Connector/Python: `pip install mariadb`
# 2. Replace placeholders with your database credentials
db_client = MariaDBClient(
    host="pvaultdb.rasp",
    port=3306,
    database="pvault",
    user="pvault",
    password="pvault"
)

# data = {"id": 1, "name": "Alice", "score": 85}
# db_client.upsert("scores", data, "id")

def db_test():
    # Select example
    results = db_client.execute("SELECT * FROM pvault.ingredients WHERE id < %s", [4])
    print(results)


    # results = db_client.read("pvault.ingredients") #, columns=["name", "score"], where_clause="score > %s", params=[70])
    # print(results)


def spreadsheet_test():
    # **How to use the class**

    # 1. Get Google Sheets API Credentials: See instructions at https://gspread.readthedocs.io 
    # 2. Install dependencies: `pip install gspread oauth2client`

    credentials_file = f"{os.getenv('PWD')}/docker-compose/app/spreadsheet_credentials.json"
    reader = GoogleSheetsReader(credentials_file)

    # Example usage:
    results = reader.read_data("Perfume Personal Worksheet", "Formulas", "B147:G185")  
    print(results) 

def apps_script_test():
    # **Example Usage**

    # Replace placeholders with your actual values
    credentials_file = f"{os.getenv('PWD')}/docker-compose/app/spreadsheet_credentials.json"
    project_id = "savvy-torch-283216"
    deployment_id = "AKfycbzRmv8uO4PAZO_xOjvkv4DYJzTcZ9V6kz6CR29RfgH55_15koQKZ0WK8YOI2zKdoVVQAg"
    script_id = "15DnFNALhMuMlEPZ70t06ACYfrYVIiJKOQkcv5rnG8GaBEn1MZfFjGT3o"
    function_name = "testGetFormula"  # Make sure this function exists in your Apps Script 

    # Example with parameters
    # parameters = [10, 20]  
    # result = run_apps_script(credentials_file, project_id, script_id, function_name, parameters)

    # Example without parameters
    result = run_apps_script(credentials_file, project_id, script_id, function_name)

    print(result)

# spreadsheet_test()
apps_script_test()