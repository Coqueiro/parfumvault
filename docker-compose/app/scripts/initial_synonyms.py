import json
from constants import DB_CREDENTIALS_FILE
from db_client import MariaDBClient
from scripts.import_formulas import clean_ingredient_name
from scripts.import_spreadsheet import read_spreadsheet_materials


if __name__ == "__main__":
    sheet_ingredients = read_spreadsheet_materials(False)
    ingredient_names = [sheet_ingredients[1]
                        for sheet_ingredients in sheet_ingredients]

    sheet_ingredient_synonyms = []

    for ingredient_name in ingredient_names:
        # To check results of cleanup function
        #     print(f"       {(ingredient_name + ' '*60)[:60]} |    {clean_ingredient_name(ingredient_name)}")
        sheet_ingredient_synonyms.append({
            'ing': ingredient_name,
            'synonym': clean_ingredient_name(ingredient_name),
            'source': 'Cleanup function',
        })

    with open(DB_CREDENTIALS_FILE) as f:
        db_client = MariaDBClient(**json.load(f))

    db_client.upsert(table_name="synonyms",
                     data=sheet_ingredient_synonyms)
