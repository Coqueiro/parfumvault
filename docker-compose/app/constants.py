import os


APP_PATH = f"{os.getenv('HOME')}/Github/parfumvault/docker-compose/app"
SPREADSHEET_CREDENTIALS_FILE = f"{APP_PATH}/credentials/spreadsheet_credentials.json"
DB_CREDENTIALS_FILE = f"{APP_PATH}/credentials/db_credentials.json"
MATERIALS_FILE = f"{APP_PATH}/spreadsheet_cache/materials.json"