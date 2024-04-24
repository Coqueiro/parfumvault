from db_client import MariaDBClient
from spreadsheet_client import GoogleSheetsReader

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

# Select example
results = db_client.execute("SELECT * FROM pvault.ingredients WHERE id < %s", [4])
print(results)

# results = db_client.read("pvault.ingredients") #, columns=["name", "score"], where_clause="score > %s", params=[70])
# print(results)


# **How to use the class**

# 1. Get Google Sheets API Credentials: See instructions at https://gspread.readthedocs.io 
# 2. Install dependencies: `pip install gspread oauth2client`

reader = GoogleSheetsReader("spreadsheet_credentials.json")

# Example usage:
results = reader.read_data("Perfume Personal Worksheet", "Formulas", "B147:G185")  
print(results) 
