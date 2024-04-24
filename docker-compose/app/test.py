from __future__ import print_function
import json

import requests
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os


# https://stackoverflow.com/questions/77256994/calling-google-apps-script-functions-with-python-requested-entity-was-not-foun
def authorize_script_api(credentials_file):
    # Define the scopes required for the Google Apps Script API
    SCOPES = [
        "https://www.googleapis.com/auth/script.projects",
        "https://www.googleapis.com/auth/script.scriptapp",
        # Added. This is used for requesting Web Apps.
        "https://www.googleapis.com/auth/drive.readonly"
    ]
    creds = google.oauth2.service_account.Credentials.from_service_account_file(
        credentials_file, scopes=SCOPES)
    return creds


def list_functions(script_id, credentials):
    try:
        service = build("script", "v1", credentials=credentials)
        content = service.projects().getContent(scriptId=script_id).execute()
        if "files" in content:
            for file in content["files"]:
                if "functionSet" in file:
                    function_set = file["functionSet"]
                    if "values" in function_set:
                        for func in function_set["values"]:
                            if "name" in func:
                                print(func["name"])
    except Exception as e:
        print(f"An error occurred: {e}")


def run_function(credentials, function_name):
    try:
        # Please set your Web Apps URL.
        url = "https://script.google.com/macros/s/AKfycbz4qF_N7bbUYY3hQgDbszm6NYAoL1bqdJ7T130U1p2wMmCKGR3tFVqpesSyAB31HOlQHQ/exec"

        access_token = credentials.token

        argument = "Pineapple Gemini Base"
        url += f"?functionName={function_name}&argument={argument}"
        res = requests.get(
            url, headers={"Authorization": "Bearer " + access_token})
        print(res.text)
        print(res.content)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Authorize the script API
    script_id = "15DnFNALhMuMlEPZ70t06ACYfrYVIiJKOQkcv5rnG8GaBEn1MZfFjGT3o"
    credentials_file = f"{os.getenv('PWD')}/docker-compose/app/spreadsheet_credentials.json"

    credentials = authorize_script_api(credentials_file)

    # List functions in the Google Apps Script project
    list_functions(script_id, credentials)

    # Specify the name of the function you want to run
    # Make sure this function exists in your Apps Script
    function_name = "testGetFormula"

    # Run the specified function in the Google Apps Script project
    run_function(credentials, function_name)
