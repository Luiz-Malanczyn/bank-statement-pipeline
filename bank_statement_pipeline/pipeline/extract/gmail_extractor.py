import base64
import os
from pathlib import Path
from bank_statement_pipeline.connection.google_connector import GoogleConnector
from bank_statement_pipeline.util.logger import logger


class GmailExtractor:
    def __init__(self, label_name="faturas", output_dir="data/bronze/to_process", processed_dir="data/bronze/processed"):
        self.label_name = label_name
        self.processed_dir = Path(processed_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory set to: {self.output_dir}")
        self.service = GoogleConnector().get_gmail_service()
        logger.info("Gmail service initialized successfully.")

    def get_label_id(self):
        logger.info(f"Fetching label ID for label: '{self.label_name}'")
        results = self.service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        for label in labels:
            if label["name"].lower() == self.label_name.lower():
                logger.info(f"Label '{self.label_name}' found with ID: {label['id']}")
                return label["id"]
        logger.error(f"Label '{self.label_name}' not found.")
        raise ValueError(f"Label '{self.label_name}' not found.")

    def list_messages_with_label(self, label_id):
        logger.info(f"Listing messages with label: {self.label_name}")
        response = self.service.users().messages().list(userId="me", labelIds=[label_id]).execute()
        messages = response.get("messages", [])
        logger.info(f"Found {len(messages)} messages with label: {self.label_name}")
        return messages

    def download_pdf_attachments(self):
        logger.info("Starting PDF attachment download process.")
        label_id = self.get_label_id()
        messages = self.list_messages_with_label(label_id)
        
        if not messages:
            logger.warning("No emails found with the specified label.")
            return

        for msg in messages:
            msg_id = msg["id"]
            message = self.service.users().messages().get(userId="me", id=msg_id).execute()
            parts = message.get("payload", {}).get("parts", [])

            for part in parts:
                filename = part.get("filename")
                if filename and filename.endswith(".pdf"):
                    filepath = self.output_dir / filename
                    processed_filepath = self.processed_dir / filename

                    if processed_filepath.exists() or filepath.exists():
                        continue

                    logger.info(f"Found new attachment: {filename}")
                    attachment_id = part["body"]["attachmentId"]
                    attachment = self.service.users().messages().attachments().get(
                        userId="me", messageId=msg_id, id=attachment_id
                    ).execute()

                    file_data = base64.urlsafe_b64decode(attachment["data"].encode("UTF-8"))
                    with open(filepath, "wb") as f:
                        f.write(file_data)
                        logger.info(f"Attachment '{filename}' saved to '{filepath}'.")

