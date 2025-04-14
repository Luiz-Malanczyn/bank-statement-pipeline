# Bank Statement Pipeline

An automated pipeline to extract bank statements from Gmail, process PDF files, and load transaction data into Google Sheets.

## Overview

This project automates the following workflow:
1. Downloads PDF bank statements from Gmail using labels
2. Extracts transaction data from PDF files
3. Transforms the data into a structured format
4. Loads the data into Google Sheets

## Requirements

- Python 3.12+
- Poetry for dependency management
- Google Account with Gmail and Google Sheets access
- Required Python packages (installed via Poetry):
  - pandas
  - beautifulsoup4
  - google-api-python-client
  - pdfplumber
  - loguru
  - and more (see pyproject.toml)

## Setup

1. Clone the repository
2. Install dependencies using Poetry:
```sh
poetry install
```

3. Create configuration files:
   - Create `config/config.yaml` for general configuration
   - Create `secret/secret.yaml` for sensitive data

4. Set up Google OAuth 2.0 credentials:
   - Create a project in Google Cloud Console
   - Enable Gmail and Google Sheets APIs
   - Create OAuth 2.0 credentials
   - Add credentials to your secret.yaml file

## Configuration

### config.yaml structure
```yaml
google_sheet:
  spreadsheet_id: your_spreadsheet_id
  sheet_name: your_sheet_name
```

### secret.yaml structure
```yaml
gmail:
  client_id: your_client_id
  client_secret: your_client_secret
  token_path: secret/token.pickle
```

## Usage

Run the main pipeline script:

```sh
python -m bank_statement_pipeline.pipeline.pipeline
```

## Project Structure

```
bank_statement_pipeline/
├── connection/           # API connections
├── pipeline/            # Main pipeline components
│   ├── extract/        # Data extraction from Gmail
│   ├── transform/      # PDF processing
│   └── load/           # Google Sheets integration
├── script/             # Configuration and utilities
└── util/               # Shared utilities
```

## Features

- Gmail integration for automatic PDF download
- PDF parsing with table extraction
- Google Sheets data loading
- Configurable pipeline components
- Logging with colored output
- Error handling and retries

## Dependencies

This project uses several key libraries:
- [`GoogleConnector`](bank_statement_pipeline/connection/google_connector.py) for Gmail and Google Sheets API integration
- [`PDFToDataFrame`](bank_statement_pipeline/pipeline/transform/pdf_to_dataframe.py) for PDF processing
- [`GoogleSheetsWriter`](bank_statement_pipeline/pipeline/load/google_sheets_writer.py) for data loading