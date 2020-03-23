import os
from google.oauth2 import service_account
from googleapiclient import discovery

class DataStore:
    __service=None
    @staticmethod
    def connect_datastore():
        CLIENT_SECRETS_FILE = os.environ.get('CLIENT_SECRETS_FILE')
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        if CLIENT_SECRETS_FILE is not None:
            credentials=service_account.Credentials.from_service_account_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
            DataStore.__service = discovery.build('sheets', 'v4', credentials=credentials)
            print('Configured datastore successfully')
        else:
            raise Exception('Cannot get token file for authorizing the request')
    
    @staticmethod
    def get_sheet_instance():
        if DataStore.__service is not None:
            return DataStore.__service.spreadsheets()
        else:
            raise Exception('Sheets v4 API Service is not available now')