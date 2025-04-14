import os
from pathlib import Path
import yaml
from abc import ABC, abstractmethod
from bank_statement_pipeline.util.logger import logger

class IConfigLoader(ABC):
    @abstractmethod
    def get_config(self, key: str, default=None):
        pass

    @abstractmethod
    def get_secret(self, section: str, key: str, default=None):
        pass

class YAMLConfigLoader(IConfigLoader):
    def __init__(self, config_path=None):
        root_dir = Path(__file__).resolve().parents[2]
        self.config_path = config_path or root_dir / "config" / "config.yaml"
        self.config = self._load_yaml(self.config_path)
        secret_path = self.config.get("secret_path", str(root_dir / "secret" / "secret.yaml"))
        self.secrets = self._load_yaml(secret_path)

    def _load_yaml(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                logger.info(f"File loaded with success: {path}")
                response = yaml.safe_load(f) or {}
                return response
        except FileNotFoundError:
            logger.info(f"⚠️ File not found: {path}")
            return {}

    def get_config(self, section: str, key: str, default=None):
        return self.config.get(section, {}).get(key, default)

    def get_secret(self, section: str, key: str, default=None):
        return self.secrets.get(section, {}).get(key, default)

class ConfigLoaderFactory:
    @staticmethod
    def create_loader(loader_type="yaml"):
        if loader_type == "yaml":
            return YAMLConfigLoader()
        raise ValueError(f"Loader {loader_type} not supported.")
    
def load_config():
    loader = ConfigLoaderFactory.create_loader()
    return loader
