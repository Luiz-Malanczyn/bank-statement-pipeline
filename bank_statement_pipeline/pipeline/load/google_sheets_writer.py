import pandas as pd
from datetime import datetime
from bank_statement_pipeline.connection.google_connector import GoogleConnector
from bank_statement_pipeline.util.logger import logger


class GoogleSheetsWriter:
    def __init__(self, spreadsheet_id, sheet_name="Página1"):
        self.service = GoogleConnector().get_sheets_service()
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        logger.info(f"Google Sheets Writer initialized for spreadsheet ID: {self.spreadsheet_id}, sheet name: '{self.sheet_name}'.")

    def get_existing_dates(self, column="A"):
        """Returns a set of date strings (YYYY-MM-DD) already in the sheet's source_date column."""
        range_ = f"{self.sheet_name}!{column}:{column}"
        logger.info(f"Fetching existing dates from column '{column}'.")
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_
        ).execute()
        values = result.get("values", [])
        existing_dates = {row[0] for row in values if row}
        logger.info(f"Found {len(existing_dates)} existing date(s) in the sheet.")
        return existing_dates

    def get_last_row(self, column="A"):
        range_ = f"{self.sheet_name}!{column}:{column}"
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_
        ).execute()
        values = result.get("values", [])
        return len(values) + 1

    def write_dataframe(self, df: pd.DataFrame, include_header=True):
        if "source_date" not in df.columns:
            logger.warning("DataFrame is missing 'source_date' column. Aborting write.")
            return

        existing_dates = self.get_existing_dates()
        logger.info("Filtering rows with new dates not yet in the sheet.")

        filtered_df = df[~df["source_date"].isin(existing_dates)]

        if filtered_df.empty:
            logger.info("No new dates found. Nothing to write.")
            return

        logger.info(f"{len(filtered_df)} new row(s) will be written to the sheet.")

        start_row = self.get_last_row()
        start_cell = f"A{start_row}"
        values = [filtered_df.columns.tolist()] + filtered_df.values.tolist() if include_header else filtered_df.values.tolist()
        range_ = f"{self.sheet_name}!{start_cell}"
        body = {"values": values}

        result = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        updated = result.get("updatedCells", 0)
        logger.info(f"{updated} cell(s) updated in Google Sheets from cell '{start_cell}'.")
