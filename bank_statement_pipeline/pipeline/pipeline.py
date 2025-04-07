from bank_statement_pipeline.connection.gmail_connection import GmailConnector

if __name__ == '__main__':
    connector = GmailConnector()
    service = connector.authenticate()
    print(service.users().messages().list(userId="me").execute())