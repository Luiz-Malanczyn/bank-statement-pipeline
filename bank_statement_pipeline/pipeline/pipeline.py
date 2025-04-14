from prefect import flow, task
from pathlib import Path
import pandas as pd

from bank_statement_pipeline.script.load_config import load_config
from bank_statement_pipeline.pipeline.extract.gmail_extractor import GmailExtractor
from bank_statement_pipeline.pipeline.transform.pdf_to_dataframe import PDFToDataFrame
from bank_statement_pipeline.pipeline.load.google_sheets_writer import GoogleSheetsWriter
from bank_statement_pipeline.util.logger import logger

@task
def extract_pdfs():
    logger.info("🔍 Starting Gmail PDF extraction...")
    extractor = GmailExtractor()
    extractor.download_pdf_attachments()
    logger.info("✅ Gmail PDF extraction completed.")

@task
def transform_pdfs_to_dataframe(bronze_dir: str = "data/bronze/to_process") -> pd.DataFrame:
    if not list(Path(bronze_dir).glob("Nubank_*.pdf")):
        logger.warning("⚠️ No PDF files to process.")
        return pd.DataFrame()
    
    logger.info("🔄 Files found, starting PDF to DataFrame transformation...")
    all_rows = []

    for pdf_file in Path(bronze_dir).glob("Nubank_*.pdf"):
        logger.info(f"📄 Processing file: {pdf_file.name}")
        try:
            transformer = PDFToDataFrame(pdf_file)
            tables = transformer.extract_table()
            df = transformer.convert_to_dataframe(tables)
            if not df.empty:
                all_rows.append(df)
                logger.info(f"✅ Data extracted from {pdf_file.name} with {len(df)} rows.")
            else:
                logger.warning(f"⚠️ No data extracted from {pdf_file.name}.")
        except Exception as e:
            logger.error(f"❌ Failed to process {pdf_file.name}: {e}")

    if all_rows:
        final_df = pd.concat(all_rows, ignore_index=True)
        logger.info(f"📊 Total rows consolidated: {len(final_df)}")
        return final_df
    else:
        logger.warning("⚠️ No data found in any PDF.")
        return pd.DataFrame()

@task
def load_to_google_sheets(df: pd.DataFrame, spreadsheet_id: str, sheet_name: str):
    logger.info("🚀 Starting data load to Google Sheets...")
    loader = GoogleSheetsWriter(spreadsheet_id, sheet_name)
    loader.write_dataframe(df)
    logger.info("✅ Data load to Google Sheets completed.")

@flow(name="Nubank Pipeline Flow")
def run_pipeline():
    logger.info("📦 Bank statement pipeline...")

    config = load_config()
    spreadsheet_id = config.get_config("google_sheet", "spreadsheet_id")
    sheet_name = config.get_config("google_sheet", "sheet_name")

    extract_pdfs()
    df = transform_pdfs_to_dataframe()

    if not df.empty:
        load_to_google_sheets(df, spreadsheet_id, sheet_name)
    else:
        logger.warning("⛔ No data to load into Google Sheets.")

    logger.info("🏁 Bank statement pipeline finished.")
