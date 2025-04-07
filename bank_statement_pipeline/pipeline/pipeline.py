# pipeline.py
from bank_statement_pipeline.script.load_config import load_config
from bank_statement_pipeline.pipeline.extract.outlook_email_extractor import OutlookEmailExtractor
from bank_statement_pipeline.util.logger import logger

config_loader = load_config()

username = config_loader.get_secret("outlook", "username")
client_id = config_loader.get_secret("outlook", "client_id")
tenant_id = config_loader.get_secret("outlook", "tenant_id")

extractor = OutlookEmailExtractor(
    client_id=client_id,
    tenant_id=tenant_id,
    username=username
)

extractor.connect()
attachments = extractor.fetch_attachments()
logger.info(f"📎 Total de emails coletados: {len(attachments)}")
extractor.disconnect()
