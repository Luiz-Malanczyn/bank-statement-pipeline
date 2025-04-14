import pandas as pd
import pdfplumber
import logging
import re
from pathlib import Path
from bank_statement_pipeline.util.logger import logger
from datetime import datetime

logging.getLogger("pdfminer").setLevel(logging.ERROR)

class PDFToDataFrame:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.processed_dir = Path("data/bronze/processed")
        if not self.pdf_path.exists():
            logger.error(f"PDF file not found: {self.pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        logger.info(f"PDF file found: {self.pdf_path}")

        self.source_date = self._extract_date_from_filename()
        logger.info(f"Extracted date from filename: {self.source_date}")

    def _extract_date_from_filename(self) -> str:
        match = re.search(r"Nubank_(\d{4}-\d{2}-\d{2})\.pdf", self.pdf_path.name)
        if match:
            return match.group(1)
        else:
            logger.warning(f"Could not extract date from filename: {self.pdf_path.name}")
            return "unknown"

    def extract_table(self):
        regex_pattern = r"TRANSAÇÕES DE \d{2} \w{3} A \d{2} \w{3}"
        transaction_tables = []
        logger.info(f"Starting table extraction from PDF: {self.pdf_path}")

        with pdfplumber.open(self.pdf_path) as pdf:
            logger.info(f"PDF opened successfully: {self.pdf_path}")
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                lines = [line.strip() for line in text.split("\n")]

                if any(re.search(regex_pattern, line) for line in lines):
                    logger.info(f"Transaction table found on page {page_number}")
                    transaction_tables.append(page.extract_tables())

            if transaction_tables:
                logger.info(f"Extracted {len(transaction_tables)} transaction tables from PDF.")
            else:
                logger.info("No transaction tables found in the PDF.")
            return transaction_tables

    def convert_to_dataframe(self, tables):
        rows = []
        regex_with_parcela = r"(\d{2}) (\w{3}) (.+?) - (Parcela \d+/\d+) (R\$|US\$|€) (\d+,\d{2})"
        regex_without_parcela = r"(\d{2}) (\w{3}) (.+?) (R\$|US\$|€) (\d+,\d{2})"
        logger.info("Starting conversion of extracted tables to DataFrame.")

        entries = [entry[0] for group in tables for item in group for entry in item]
        logger.info(f"Total entries found in tables: {len(entries)}")

        for entry in entries:
            match = re.match(regex_with_parcela, entry)
            if match:
                day, month, description, payment, coin, value = match.groups()
            else:
                match = re.match(regex_without_parcela, entry)
                if match:
                    day, month, description, coin, value = match.groups()
                    payment = "In cash"
                else:
                    continue

            amount = float(value.replace(",", "."))
            rows.append([
                self.source_date,
                day,
                month,
                description.strip(),
                payment,
                coin,
                amount
            ])

        if rows:
            logger.info(f"Successfully parsed {len(rows)} rows into DataFrame.")
        else:
            logger.warning("No valid rows were parsed into the DataFrame.")

        df = pd.DataFrame(
            rows,
            columns=["source_date", "day", "month", "description", "payment", "coin", "amount"]
        )
        logger.info("DataFrame created successfully.")

        new_path = self.processed_dir / self.pdf_path.name
        self.pdf_path.rename(new_path)
        logger.info(f"Moved processed PDF to: {new_path}")

        return df
