import os
from google.oauth2 import service_account
from googleapiclient import discovery
import json

class DataStore:
    __service=None
    @staticmethod
    def connect_datastore():
        CLIENT_SECRETS_FILE = os.environ.get('CLIENT_SECRETS_FILE')
        CLIENT_SECRET_INFO = os.environ.get('CLIENT_SECRET_INFO')
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        if CLIENT_SECRETS_FILE is not None or CLIENT_SECRET_INFO:
            try:
                if CLIENT_SECRET_INFO:
                    CLIENT_SECRET_INFO=json.loads(CLIENT_SECRET_INFO)
                    credentials=service_account.Credentials.from_service_account_info(CLIENT_SECRET_INFO, scopes=SCOPES)
                else:
                    credentials=service_account.Credentials.from_service_account_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
                DataStore.__service = discovery.build('sheets', 'v4', credentials=credentials)
                print('Configured datastore successfully')
            except Exception as e:
                print('Exception while loading and using credential json info', e)
                return
        else:
            raise Exception('Cannot get token file for authorizing the request')
    
    @staticmethod
    def get_sheet_instance():
        if DataStore.__service is not None:
            return DataStore.__service.spreadsheets()
        else:
            try:
                DataStore.connect_datastore()
                if DataStore.__service is not None:
                    return DataStore.__service.spreadsheets()
                else:
                    raise Exception('Sheets v4 API Service is not available now')
            except Exception as e:
                print('Exception while configuring datastore', e)
                raise Exception('Sheets v4 API Service is not available now')