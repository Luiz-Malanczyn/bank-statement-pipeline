# Bank Statement Pipeline

An automated ETL pipeline that extracts bank statements from Gmail, processes PDF files, and loads transaction data into Google Sheets.

## 🌟 Features

- Automated Gmail PDF attachment extraction using labels
- Intelligent PDF parsing with table detection
- Google Sheets integration for data storage
- Configurable pipeline components
- Colorized logging with detailed output
- Error handling and retry mechanisms
- Built with modern Python practices using Poetry

## 🛠️ Requirements

- Python 3.12 or higher
- Poetry for dependency management
- Google Account with:
  - Gmail API access
  - Google Sheets API access
- Required Python packages (managed by Poetry):
  - pandas
  - pdfplumber
  - google-api-python-client
  - prefect
  - loguru
  - beautifulsoup4
  - and more (see `pyproject.toml`)

## 📦 Installation

1. Clone the repository:
```sh
git clone https://github.com/Luiz-Malanczyn/bank-statement-pipeline
cd bank-statement-pipeline
```

2. Install dependencies using Poetry:
```sh
poetry install
```

## ⚙️ Configuration

### 1. Create Configuration Files

Create two configuration files in your project:

1. `config/config.yaml`:
```yaml
google_sheet:
  spreadsheet_id: your_spreadsheet_id
  sheet_name: your_sheet_name
```

2. `secret/secret.yaml`:
```yaml
gmail:
  client_id: your_client_id
  client_secret: your_client_secret
  token_path: secret/token.pickle
```

### 2. Google Cloud Setup

1. Create a project in Google Cloud Console
2. Enable required APIs:
   - Gmail API
   - Google Sheets API
3. Create OAuth 2.0 credentials:
   - Create a new OAuth 2.0 Client ID
   - Download client credentials
   - Add credentials to `secret.yaml`

## 📂 Project Structure

```
bank_statement_pipeline/
├── connection/           # API connection handlers
│   └── google_connector.py
├── pipeline/            # Core pipeline components
│   ├── extract/        # Gmail data extraction
│   ├── transform/      # PDF processing logic
│   └── load/           # Google Sheets integration
├── script/             # Configuration utilities
│   └── load_config.py
└── util/               # Shared utilities
    └── logger.py
```

## 🚀 Usage

Run the pipeline using either:

```sh
# Using Python module
python -m bank_statement_pipeline.pipeline.pipeline

# Or using the main script
python main.py
```

## 🔄 Pipeline Flow

1. **Extract**: Downloads PDF bank statements from Gmail using specified labels
2. **Transform**: Processes PDF files to extract transaction data
3. **Load**: Writes processed data to Google Sheets

## 🔒 Security

- Sensitive credentials are stored in `secret.yaml` (gitignored)
- OAuth2 tokens are securely managed
- Uses environment-based configuration

## 🐳 Docker Support

Build and run using Docker:

```sh
docker build -t bank-statement-pipeline .
docker run -v $(pwd)/config:/app/config -v $(pwd)/secret:/app/secret bank-statement-pipeline
```