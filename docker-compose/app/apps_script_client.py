from __future__ import print_function

import google.auth
import requests
from googleapiclient.discovery import build


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


def run_function(script_url, script_id, function_name, argument, credentials):
    try:
        service = build("script", "v1", credentials=credentials)
        service.projects().getContent(scriptId=script_id).execute()
        access_token = credentials.token

        url = f"{script_url}?functionName={function_name}&argument={argument}"
        res = requests.get(
            url, headers={"Authorization": "Bearer " + access_token})

        return res.content.decode('utf-8')

    except Exception as e:
        print(f"An error occurred: {e}")
