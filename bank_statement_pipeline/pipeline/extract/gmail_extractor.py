import base64
import os
from pathlib import Path
from bank_statement_pipeline.connection.gmail_connector import GmailConnector
from bank_statement_pipeline.util.logger import logger


class GmailExtractor:
    def __init__(self, label_name="faturas", output_dir="data/bronze/gmail_attachments"):
        self.label_name = label_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.service = GmailConnector().authenticate()

    def get_label_id(self):
        results = self.service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        for label in labels:
            if label["name"].lower() == self.label_name.lower():
                return label["id"]
        raise ValueError(f"Label '{self.label_name}' não encontrada.")

    def list_messages_with_label(self, label_id):
        response = self.service.users().messages().list(userId="me", labelIds=[label_id]).execute()
        messages = response.get("messages", [])
        return messages

    def download_pdf_attachments(self):
        label_id = self.get_label_id()
        messages = self.list_messages_with_label(label_id)
        
        if not messages:
            logger.info("Nenhum e-mail encontrado com o marcador fornecido.")
            return

        for msg in messages:
            msg_id = msg["id"]
            message = self.service.users().messages().get(userId="me", id=msg_id).execute()
            parts = message.get("payload", {}).get("parts", [])
            for part in parts:
                filename = part.get("filename")
                if filename and filename.endswith(".pdf"):
                    attachment_id = part["body"]["attachmentId"]
                    attachment = self.service.users().messages().attachments().get(
                        userId="me", messageId=msg_id, id=attachment_id
                    ).execute()

                    file_data = base64.urlsafe_b64decode(attachment["data"].encode("UTF-8"))
                    filepath = self.output_dir / filename
                    with open(filepath, "wb") as f:
                        f.write(file_data)
                        logger.info(f"Anexo '{filename}' salvo em '{filepath}'.")