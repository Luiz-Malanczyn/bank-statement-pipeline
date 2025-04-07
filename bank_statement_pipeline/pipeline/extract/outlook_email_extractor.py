from bank_statement_pipeline.pipeline.extract.base_email_extractor import BaseEmailExtractor
from bank_statement_pipeline.connection.outlook_connection import OutlookConnection

class OutlookEmailExtractor(BaseEmailExtractor):
    def __init__(self, client_id, tenant_id, username):
        self.connection = OutlookConnection(client_id, tenant_id, username)

    def connect(self):
        self.connection.connect()

    def fetch_attachments(self):
        messages = self.connection.get("me/messages", params={"$top": 5, "$select": "subject,receivedDateTime"})
        emails = []

        for msg in messages.get("value", []):
            subject = msg.get("subject", "(sem assunto)")
            date = msg.get("receivedDateTime")
            emails.append({"subject": subject, "date": date})

        return emails

    def disconnect(self):
        self.connection.disconnect()
