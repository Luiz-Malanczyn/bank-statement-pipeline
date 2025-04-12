from bank_statement_pipeline.pipeline.extract.gmail_extractor import GmailExtractor
from bank_statement_pipeline.pipeline.transform.pdf_to_dataframe import PDFToDataFrame

if __name__ == '__main__':
    # extractor = GmailExtractor()
    # arquivos_salvos = extractor.download_pdf_attachments()
    transformer = PDFToDataFrame("data/bronze/gmail_attachments/Nubank_2025-04-02.pdf")
    tables = transformer.extract_table()
    transactions_df = transformer.convert_to_dataframe(tables)
    print(transactions_df)