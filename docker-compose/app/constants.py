import os


APP_PATH = f"{os.getenv('HOME')}/Github/parfumvault/docker-compose/app"
SPREADSHEET_CREDENTIALS_FILE = f"{APP_PATH}/credentials/spreadsheet_credentials.json"
DB_CREDENTIALS_FILE = f"{APP_PATH}/credentials/db_credentials.json"
SPREADSHEET_CACHE_FILE = f"{APP_PATH}/cache/spreadsheet/materials.json"
DB_CACHE_FOLDER = f"{APP_PATH}/db"
DB_INGREDIENT_SYNONYMS_CACHE_FILE = f"{DB_CACHE_FOLDER}/db_ingredient_synonyms.json"
DB_INGREDIENT_IDS_CACHE_FILE = f"{DB_CACHE_FOLDER}/db_ingredient_ids.json"
DB_NEW_INGREDIENT_SYNONYMS_BUFFER_FILE = f"{DB_CACHE_FOLDER}/new_ingredient_synonyms.json"

IS_ONLINE = True
