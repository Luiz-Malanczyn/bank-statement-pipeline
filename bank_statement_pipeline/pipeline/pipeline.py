from bank_statement_pipeline.script.load_config import load_config

from bank_statement_pipeline.pipeline.extract.gmail_extractor import GmailExtractor
from bank_statement_pipeline.pipeline.transform.pdf_to_dataframe import PDFToDataFrame
from bank_statement_pipeline.pipeline.load.google_sheets_writer import GoogleSheetsWriter

if __name__ == '__main__':
    config_loader = load_config()
    spreadsheet_id = config_loader.get_config("google_sheet", "spreadsheet_id")
    sheet_name = config_loader.get_config("google_sheet", "sheet_name")
    
    extractor = GmailExtractor()
    arquivos_salvos = extractor.download_pdf_attachments()
    transformer = PDFToDataFrame("data/bronze/Nubank_2025-04-02.pdf")
    tables = transformer.extract_table()
    transactions_df = transformer.convert_to_dataframe(tables)
    loader = GoogleSheetsWriter(spreadsheet_id, sheet_name)
    loader.write_dataframe(transactions_df)