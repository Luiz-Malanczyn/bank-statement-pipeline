import pandas as pd
from bank_statement_pipeline.connection.google_connector import GoogleConnector
from bank_statement_pipeline.util.logger import logger

class GoogleSheetsWriter:
    def __init__(self, spreadsheet_id, sheet_name="Página1"):
        self.service = GoogleConnector().get_sheets_service()
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name

    def get_last_row(self, column="A"):
        range_ = f"{self.sheet_name}!{column}:{column}"
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_
        ).execute()
        values = result.get("values", [])
        return len(values) + 1

    def write_dataframe(self, df: pd.DataFrame, include_header=True):
        start_row = self.get_last_row()
        start_cell = f"A{start_row}"

        values = [df.columns.tolist()] + df.values.tolist() if include_header else df.values.tolist()
        
        range_ = f"{self.sheet_name}!{start_cell}"
        body = {"values": values}

        result = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        updated = result.get("updatedCells", 0)
        logger.info(f"{updated} células atualizadas a partir de {start_cell} na planilha '{self.sheet_name}'.")