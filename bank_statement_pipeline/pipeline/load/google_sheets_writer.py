from bank_statement_pipeline.connection.google_connector import GoogleConnector
from bank_statement_pipeline.util.logger import logger

class GoogleSheetsWriter:
    def __init__(self, spreadsheet_id, sheet_name="Página1"):
        self.service = GoogleConnector().get_sheets_service()
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name

    def write_rows(self, values, start_cell="A1", clear_before=True):
        range_ = f"{self.sheet_name}!{start_cell}"
        
        if clear_before:
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}"
            ).execute()
            logger.info(f"Conteúdo da aba '{self.sheet_name}' limpo com sucesso.")

        body = {"values": values}
        result = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        updated = result.get("updatedCells", 0)
        logger.info(f"{updated} células atualizadas na planilha '{self.sheet_name}'.")

