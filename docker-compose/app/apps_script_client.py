import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
import google.auth.transport.requests
import requests
import json

SCOPES = ['https://www.googleapis.com/auth/script.projects']
API_SERVICE_NAME = 'script'
API_VERSION = 'V1'


def getAccessToken():
    # Please set your value.
    SCOPES = [
        "https://www.googleapis.com/auth/script.projects",
        "https://www.googleapis.com/auth/script.scriptapp",
        # Added. This is used for requesting Web Apps.
        "https://www.googleapis.com/auth/drive.readonly"
    ]
    SERVICE_ACCOUNT_FILE = f"{os.getenv('PWD')}/docker-compose/app/spreadsheet_credentials.json"

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive.readonly"])
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


# https://medium.com/google-cloud/executing-google-apps-script-with-service-account-3752f4e3df8c
def run_apps_script(*args, **kwargs):
    webApps_url = "https://script.google.com/macros/s/AKfycbzRmv8uO4PAZO_xOjvkv4DYJzTcZ9V6kz6CR29RfgH55_15koQKZ0WK8YOI2zKdoVVQAg/dev"
    access_token = getAccessToken()
    # POST method
    # credentials_file = "spreadsheet_credentials.json"
    # project_id = "savvy-torch-283216"
    # script_id = "15DnFNALhMuMlEPZ70t06ACYfrYVIiJKOQkcv5rnG8GaBEn1MZfFjGT3o"
    function_name = "testGetFormula"
    # arguments = {"range": "'Sheet1'!A1:A2", "values": [
    #     ["sample value 1"], ["sample value 2"]]}
    arguments = {}
    url = f'{webApps_url}?functionName={function_name}&arguments={json.dumps(arguments)}'
    res = requests.get(url, json.dumps(arguments), headers={
                       "Authorization": "Bearer " + access_token})
    print(res.text)
    return res


def run_apps_script_v2(credentials_file, project_id, script_id, function_name, parameters=[]):
    """Runs a Google Apps Script function and returns the result.

    Args:
        credentials_file (str): Path to your Apps Script API credentials JSON file.
        project_id (str): The Project ID of your Apps Script project.
        script_id (str): The Script ID of your Apps Script project.
        function_name (str): The name of the Apps Script function to execute.
        parameters (list, optional): A list of parameters to pass to the function.

    Returns:
        The return value of the Apps Script function, or None if an error occurs.
    """

    credentials = service_account.Credentials.from_service_account_file(
        credentials_file, scopes=SCOPES)
    delegated_creds = credentials.with_subject("kartgarcia@gmail.com")
    # delegated_creds = credentials.with_subject("382867223659-compute@developer.gserviceaccount.com")

    service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Create the request body
    request = {"function": function_name,
               "parameters": parameters, "devMode": True}

    # Execute the Apps Script function
    try:
        response = service.scripts().run(body=request, scriptId=script_id).execute()

        if 'error' in response:
            error_message = response['error']['details'][0]['errorMessage']
            print(f"Apps Script error: {error_message}")
            return None
        else:
            return response.get('response').get('result')
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
