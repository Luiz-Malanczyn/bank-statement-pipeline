import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from bank_statement_pipeline.script.load_config import load_config
from bank_statement_pipeline.util.logger import logger

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets"
]

class GoogleConnector:
    def __init__(self):
        config_loader = load_config()
        self.client_id = config_loader.get_secret("gmail", "client_id")
        self.client_secret = config_loader.get_secret("gmail", "client_secret")
        self.token_path = Path(config_loader.get_secret("gmail", "token_path", "secret/token.pickle"))
        self.creds = None

    def authenticate(self):
        if self.token_path.exists():
            with open(self.token_path, "rb") as token:
                self.creds = pickle.load(token)
                logger.info("Loading token from pickle file.")

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                logger.info("Google token renewed.")
            else:
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token"
                        }
                    },
                    SCOPES
                )
                self.creds = flow.run_local_server(port=0)
                logger.info("New authentication token generated with success.")

            with open(self.token_path, "wb") as token:
                pickle.dump(self.creds, token)
                logger.info("Token saved in the pickle file.")
    
    def get_service(self, service_name: str, version: str):
        if not self.creds:
            self.authenticate()
        return build(service_name, version, credentials=self.creds)
    
    def get_gmail_service(self):
        return self.get_service("gmail", "v1")
    
    def get_sheets_service(self):
        return self.get_service("sheets", "v4")
