import gspread
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheetsReader:
    def __init__(self, credentials_file):
        """
        Initializes the Google Sheets reader.

        Args:
            credentials_file (str): Path to the JSON file containing 
                                    Google Sheets API credentials.
        """
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file, scope)
        self.client = gspread.authorize(credentials)

    def read_data(self, spreadsheet_name, sheet_name, range):
        """
        Reads data from the specified sheet and range.

        Args:
            sheet_name (str): Name of the worksheet.
            range (str): Range of cells in A1 notation (e.g., 'A1:D10').

        Returns:
            list: A list of lists, where each inner list represents a row of data.
        """

        try:
            spreadsheet = self.client.open(spreadsheet_name)  # Open by sheet title
            worksheet = spreadsheet.worksheet(sheet_name)
            data = worksheet.get(range)
            return data
        except Exception as e:
            print(f"Error reading data from Google Sheets: {e}")
            return None
