import hashlib
import json
import pydoc
import re

import inquirer
import nltk
import PyPDF2
from db_client import MariaDBClient
from nltk.corpus import stopwords
from nltk.metrics.distance import jaro_winkler_similarity
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from constants import DB_CREDENTIALS_FILE, APP_PATH

FORMULAS_PATH = f"{APP_PATH}/formulas/"
FORMULA_FILES = [
    # f"{FORMULAS_PATH}Perfume Archive/Vibe Formulas/1881 MEN - IMF022.pdf",
    f"{FORMULAS_PATH}Perfume Archive/Vibe Formulas/XERYUS ROUGE HOMME - IMF237.pdf",
    f"{FORMULAS_PATH}Perfume Archive/Vibe Formulas/XS PACO RAB. 1994 - IMF238.pdf",
]


nltk.download('stopwords')

# https://spotintelligence.com/2022/12/19/text-similarity-python/
# https://www.nltk.org/api/nltk.metrics.distance.html


def compute_similarity(text1, text2):
    # similarity = jaro_similarity(text1, text2)
    similarity = jaro_winkler_similarity(text1, text2, p=0.04)
    return similarity

# 0.000001: 9/10
# 0.01: 9/10
# 0.1: 14/17


def text_similarity(text1, text2):
    tokens1 = word_tokenize(text1)
    tokens2 = word_tokenize(text2)
    lemmatizer = WordNetLemmatizer()
    tokens1 = [lemmatizer.lemmatize(token) for token in tokens1]
    tokens2 = [lemmatizer.lemmatize(token) for token in tokens2]

    stop_words = stopwords.words('english')
    tokens1 = ' '.join([token for token in tokens1 if token not in stop_words])
    tokens2 = ' '.join([token for token in tokens2 if token not in stop_words])

    similarity = compute_similarity(tokens1, tokens2)

    return similarity


def find_closest_match(target_string, list_of_strings):
    """
    Finds the string in a list with the smallest Levenshtein distance from a target string.
    """
    max_similarity = float(0)
    closest_string = None

    for string in list_of_strings:
        similarity = text_similarity(target_string, string)
        if similarity > max_similarity:
            max_similarity = similarity
            closest_string = string

    return closest_string, max_similarity


def filter_text(text, pattern):
    result = re.sub(pattern, "", text, flags=re.MULTILINE)
    return result


def preprocess(text, source='Perfume Archive/Vibe Formulas'):
    filtered_text = text

    if source == 'Perfume Archive/Vibe Formulas':
        filtered_text = filter_text(filtered_text, r"^TOTAL[\w\W]*$")
        filtered_text = filter_text(filtered_text, r"PerfumerArchive\.com")
        filtered_text = filter_text(filtered_text, r"^\W+")
    else:
        pass

    return filtered_text


def clean_ingredient_name(ingredient_name):
    return filter_text(
        filter_text(
            filter_text(
                ingredient_name.upper(),
                r"[ (\-](SYMRISE|GIVAUDAN|FIRMENICH|ROBERTET|BEDOUKIAN|DEPR|NATURAL|IFF|FIRM|SYNA|SODA|KAO|GIV|ROBER|DPG|IPM|SYM|DRT|FCC|®|@)"
            ), r"((([ ]?\([^()]*\)|[., -])+$)|[()])",
        ), r"[., -]+$",
    )


def get_db_ingredient_synonyms(db_client):
    synonyms_rows = db_client.execute(
        'SELECT ing as name, synonym FROM pvault.synonyms')
    
    db_ingredient_synonyms = {}
    
    for synonyms_row in synonyms_rows:
        db_ingredient_synonyms[synonyms_row['synonym']] = synonyms_row['name']
        
    return db_ingredient_synonyms


def get_db_ingredient_ids(db_client):
    ingredients_rows = db_client.execute(
        'SELECT id, name FROM pvault.ingredients')
    
    db_ingredient_ids = {}
    
    for ingredients_row in ingredients_rows:
        db_ingredient_ids[ingredients_row['name']] = ingredients_row['id']
        
    return db_ingredient_ids


def match_ingredients(target_string, db_ingredients):
    closest_string, max_similarity = find_closest_match(
        target_string, db_ingredients)

    return closest_string, max_similarity


def extract_perfume_formula(pdf_path):
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    raw_file_extract = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        raw_file_extract += '\n' + page.extract_text()

    preprocess_text = preprocess(raw_file_extract)

    pattern = r"([\w0-9 ()-.%/,]+)[ ]+([0-9.]+)$"
    ingredients_text = re.findall(pattern, preprocess_text, flags=re.MULTILINE)

    return ingredients_text, raw_file_extract


def extract_structure_perfume_formula(pdf_path):
    formula_ingredients_result, raw_file_extract = extract_perfume_formula(pdf_path)
    formula_ingredients = []
    for formula_ingredient_result in formula_ingredients_result:
        name, quantity = formula_ingredient_result
        formula_ingredients.append({
            'name': name.upper(),
            'quantity': float(quantity),
        })
    return formula_ingredients, raw_file_extract


def ingredient_match_inquiry(formula_ingredient, db_ingredient, similarity, raw_file_extract):
    choices = [f"Yes ({round(similarity,2)})", "No", "Read extract"]
    is_match_question = inquirer.List(
        "question",
        message=f"Formula ingredient '{formula_ingredient}' == '{db_ingredient}' [db]",
        choices=choices,
    )
    is_match_answer = inquirer.prompt([is_match_question])
    choice = is_match_answer["question"]

    if choice == choices[0]:
        return db_ingredient
    elif choice == choices[1]:
        proposed_ingredient_name = clean_ingredient_name(
            formula_ingredient).title()
        text_input = input(
            f"Enter db ingredient name [{proposed_ingredient_name}]: ")
        if len(text_input) > 0:
            return text_input
        else:
            return proposed_ingredient_name
    elif choice == choices[2]:
        pydoc.pager(f"{raw_file_extract}\n{formula}")
        return ingredient_match_inquiry(formula_ingredient, db_ingredient, similarity, raw_file_extract)


def translate_formula(formula, db_ingredient_synonyms, raw_file_extract):
    translated_formula = {}
    new_ingredient_synonyms = {}
    ingredient_synonyms = db_ingredient_synonyms.keys()

    for formula_ingredient in formula:
        closest_string, max_similarity = match_ingredients(
            formula_ingredient['name'], ingredient_synonyms)
        closest_db_ingredient = db_ingredient_synonyms[closest_string]
        if max_similarity == 1:
            translated_formula[closest_db_ingredient] = formula_ingredient['quantity']
        else:
            ingredient_answer = ingredient_match_inquiry(
                formula_ingredient['name'], closest_db_ingredient, max_similarity, raw_file_extract)
            translated_formula[ingredient_answer] = formula_ingredient['quantity']
            new_ingredient_synonyms[formula_ingredient['name']] = ingredient_answer
            

    return translated_formula, new_ingredient_synonyms


def insert_new_ingredient_synonyms(new_ingredient_synonyms, formula_name, db_client):
    if len(new_ingredient_synonyms) > 0:
        synonyms_dict = []
        for synonym, ing in new_ingredient_synonyms.items():
            synonyms_dict.append({
                'synonym': synonym,
                'ing': ing,
                'source': f"Formula: {formula_name}",
            })
        
        db_client.upsert(table_name="synonyms", data=synonyms_dict)


def insert_new_formula(translated_formula, relative_formula_path, formula_file, raw_file_extract, db_ingredient_ids, db_client):
    fid = hashlib.sha256(bytes(relative_formula_path, 'utf-8')).hexdigest()[:40]
    formulasMetaData_data = []
    formulasMetaData_data.append({
        'name': formula_file,
        'fid': fid,
        'sex': '',
        'notes': raw_file_extract, # Raw text extracted from PDF
        'catClass': 'cat4', # Fine fragrance category
        'status': 2, # Under evaluation
    })
    db_client.upsert(table_name="formulasMetaData", data=formulasMetaData_data)
    formula_id_result = formula_id = db_client.execute(
        f"SELECT id FROM pvault.formulasMetaData WHERE fid = '{fid}'"
    )
    formula_id = formula_id_result[0]['id']

    formulasTags_data = []
    formulasTags_data.append({
        'formula_id': formula_id,
        'tag_name': '/'.join(relative_formula_path.split('/')[:-1]), # Folder of formula file
    })
    formulasTags_data[0]['tag_hash'] = int(str(int(hashlib.sha256(bytes(
        formulasTags_data[0]['tag_name']+str(formulasTags_data[0]['formula_id']), 'utf-8')
    ).hexdigest(), 16))[:9])
    db_client.upsert(table_name="formulasTags", data=formulasTags_data)
    
    formulas_data = []
    formula_history_data = []
    for formula_ingredient, quantity in translated_formula.items():
        fid_ingredient_hash = int(str(int(hashlib.sha256(bytes(fid+formula_ingredient, 'utf-8')).hexdigest(), 16))[:9])
        formulas_data.append({
            'fid': fid,
            'name': formula_file,
            'ingredient': formula_ingredient,
            'ingredient_id': db_ingredient_ids.get(formula_ingredient),
            'quantity': quantity,
            'fid_ingredient_hash': fid_ingredient_hash,
        })
        formula_history_data.append({
            'fid': fid,
            'change_made': f"ADDED: {formula_ingredient} {quantity}g @100%",
            'user': 'import_formulas',
            'fid_ingredient_hash': fid_ingredient_hash,
        })
    db_client.upsert(table_name="formulas", data=formulas_data)
    db_client.upsert(table_name="formula_history", data=formula_history_data)


def simple_dict_table(dictionary):
    table = ''
    first_column_size = max([0]+[len(value) for value in dictionary.keys()])
    for key, value in dictionary.items():
        table += f"   {(key + ' '*first_column_size)[:first_column_size]} | {value}\n"
    return table


if __name__ == "__main__":
    INSERT_PROMPT = True
    
    with open(DB_CREDENTIALS_FILE) as f:
        db_client = MariaDBClient(**json.load(f))
    db_ingredient_synonyms = get_db_ingredient_synonyms(db_client)
    db_ingredient_ids = get_db_ingredient_ids(db_client)
    
    for formula_path in FORMULA_FILES:
        formula, raw_file_extract = extract_structure_perfume_formula(formula_path)

        translated_formula, new_ingredient_synonyms = translate_formula(
            formula, db_ingredient_synonyms, raw_file_extract)

        relative_formula_path = formula_path.replace(FORMULAS_PATH, '')
        formula_file = relative_formula_path.split('/')[-1].replace('.pdf', '')

        validation_text = f"""{formula_file}
        
{simple_dict_table(translated_formula)}
Total quantity: {round(sum(translated_formula.values()),2)}\n
{simple_dict_table(new_ingredient_synonyms)}"""

        pydoc.pager(validation_text)
        print(validation_text)
        
        insert_answer = False
        if INSERT_PROMPT:
            repeat_choice = "Read extract"
            insert_answer = repeat_choice
            while insert_answer == repeat_choice:
                insert_question = inquirer.List(
                    "question",
                    message=f'Insert formula and new ingredients?',
                    choices=[True, False, repeat_choice],
                )
                insert_answer = inquirer.prompt([insert_question])["question"]
            
            if insert_answer==repeat_choice:
                # TODO: Check why regex got the result
                # TODO: Insert option to correct data (ask which ingredient and then if new quantity or name)
                pass
            elif not INSERT_PROMPT or insert_answer:
                insert_new_ingredient_synonyms(new_ingredient_synonyms, formula_file, db_client)
                insert_new_formula(translated_formula, relative_formula_path, formula_file, raw_file_extract, db_ingredient_ids, db_client)
                db_ingredient_synonyms = {
                    **db_ingredient_synonyms,
                    **new_ingredient_synonyms,
                }
        
        

# Create readers for different kinds of pdfs depending on pdf properties, including path

# Steps:
# TODO: 1. Formula extraction
# 2. Ingredient matching
# 3. Formula writing to database

# We start with 2 for a single formula, then 3, then 1 to scale to writing all formulas
