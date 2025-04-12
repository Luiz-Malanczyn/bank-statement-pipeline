import pandas as pd
import pdfplumber
import logging
import re
from pathlib import Path
from bank_statement_pipeline.util.logger import logger

logging.getLogger("pdfminer").setLevel(logging.ERROR)

class PDFToDataFrame:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"Arquivo PDF não encontrado: {self.pdf_path}")

    def extract_table(self):
        regex_pattern = r"TRANSAÇÕES DE \d{2} \w{3} A \d{2} \w{3}"
        transaction_tables = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                lines = [line.strip() for line in text.split("\n")]

                if any(re.search(regex_pattern, line) for line in lines):
                    transaction_tables.append(page.extract_tables())

            return transaction_tables
        return None
    
    def convert_to_dataframe(self, tables):
        rows = []
        regex_with_parcela = r"(\d{2}) (\w{3}) (.+?) - (Parcela \d+/\d+) (R\$|US\$|€) (\d+,\d{2})"
        regex_without_parcela = r"(\d{2}) (\w{3}) (.+?) (R\$|US\$|€) (\d+,\d{2})"

        entries = [entry[0] for group in tables for item in group for entry in item]

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
                    continue  # ignora se não casar com nenhum dos dois padrões

            amount = float(value.replace(",", "."))
            rows.append([day, month, description, payment, coin, amount])

        df = pd.DataFrame(rows, columns=["day", "month", "description", "payment", "coin", "amount"])
        return df
