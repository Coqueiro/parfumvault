import json
import os
import re

import inquirer
import nltk
import PyPDF2
from db_client import MariaDBClient
from nltk.corpus import stopwords
from nltk.metrics.distance import jaro_winkler_similarity
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

APP_PATH = f"{os.getenv('HOME')}/Github/parfumvault/docker-compose/app"
DB_CREDENTIALS_FILE = f"{APP_PATH}/credentials/db_credentials.json"

FORMULA_FILE = f"{APP_PATH}/formulas/Perfume Archive/Vibe Formulas/1881 MEN - IMF022.pdf"


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
            ingredient_name,
            r"(IFF|FIRM|SYNA|SODA|KAO|GIV|ROBER|DPG|IPM|SYM|DRT|FCC|®|@|Natural|Symrise|Givaudan|Firmenich)"
        ), r"[ \-\(\)]+$"
    )

def get_db_ingredient_synonyms():
    with open(DB_CREDENTIALS_FILE) as f:
        db_client = MariaDBClient(**json.load(f))

    db_ingredients_rows = db_client.execute(
        'SELECT name FROM pvault.ingredients')
    
    db_ingredients_dict = {}
    
    for db_ingredients_row in db_ingredients_rows:
        cleaned_name = clean_ingredient_name(db_ingredients_row["name"]).upper()
        db_ingredients_dict[cleaned_name] = db_ingredients_row["name"]
    
    return db_ingredients_dict


def match_ingredients(target_string, db_ingredients):
    closest_string, max_similarity = find_closest_match(
        target_string, db_ingredients)

    return closest_string, max_similarity


def extract_perfume_formula(pdf_path):
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    raw_text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        raw_text += '\n' + page.extract_text()

    preprocess_text = preprocess(raw_text)

    pattern = r"([\w0-9 ()-.]+)[ ]+([0-9\.]+)$"
    ingredients_text = re.findall(pattern, preprocess_text, flags=re.MULTILINE)

    return ingredients_text


def extract_structure_perfume_formula(pdf_path):
    formula_ingredients_result = extract_perfume_formula(pdf_path)
    formula_ingredients = []
    for formula_ingredient_result in formula_ingredients_result:
        name, quantity = formula_ingredient_result
        formula_ingredients.append({
            'name': name.upper(),
            'quantity': float(quantity),
        })
    return formula_ingredients


def ingredient_match_inquiry(formula_ingredient, db_ingredient, similarity):
    choices = [f"Yes ({round(similarity,2)})", "No"]
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
        proposed_ingredient_name = clean_ingredient_name(formula_ingredient).title()
        text_input = input(f"Enter db ingredient name [{proposed_ingredient_name}]: ")
        if len(text_input) > 0:
            return text_input
        else:
            return proposed_ingredient_name


def translate_formula(formula, db_ingredient_synonyms_dict):
    translated_formula = {}
    new_ingredient_synonyms = {}
    ingredient_synonyms = db_ingredient_synonyms_dict.keys()
    
    for formula_ingredient in formula:
        closest_string, max_similarity = match_ingredients(
            formula_ingredient['name'], ingredient_synonyms)
        closest_db_ingredient = db_ingredient_synonyms_dict[closest_string]
        if max_similarity == 1:
            translated_formula[closest_db_ingredient] = formula_ingredient['quantity'] 
        else:
            ingredient_answer = ingredient_match_inquiry(formula_ingredient['name'], closest_db_ingredient, max_similarity)
            translated_formula[ingredient_answer] = formula_ingredient['quantity']
            if ingredient_answer!=closest_db_ingredient:
                new_ingredient_synonyms[formula_ingredient['name']] = ingredient_answer
    
    return translated_formula, new_ingredient_synonyms

if __name__ == "__main__":
    db_ingredient_synonyms_dict = get_db_ingredient_synonyms()
    formula = extract_structure_perfume_formula(FORMULA_FILE)
    
    # db_ingredient_synonyms_dict is updated by this function 
    translated_formula, new_ingredient_synonyms = translate_formula(formula, db_ingredient_synonyms_dict)
    
    print(translated_formula)
    print(new_ingredient_synonyms)
    
    # We should think about reinserting the db_ingredient_synonyms_dict into the database
    # or reinsert it every N formulas
                
# IDEAS:
# If similarity = 1 approve the match (we want to avoid false positives at all costs)
# Keep track of synonyms using the pvault.synonyms and use them as additional strings to check
# Keep track of false-positives using a custom table to automatically deny match (pvault.falseIngredientMatches)
# Depending on similarity level, prompt user to check if the match is ok, 
## we can show match is similarity level is good or not show it at all if it's too bad
# If user says it's not ok, ask if there's an existing ingredient and add the name to 
## the pvault.synonyms (add the pdf name as a synonym)
# Create readers for different kinds of pdfs depending on pdf properties, including path

# Steps:
# 1. Formula extraction
# 2. Ingredient matching
# 3. Formula writing to database

# We start with 2 for a single formula, then 3, then 1 to scale to writing all formulas
