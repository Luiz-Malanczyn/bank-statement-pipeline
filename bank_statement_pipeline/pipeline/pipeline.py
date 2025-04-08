from bank_statement_pipeline.pipeline.extract.gmail_extractor import GmailExtractor

if __name__ == '__main__':
    extractor = GmailExtractor()
    arquivos_salvos = extractor.download_pdf_attachments()