import os
import msal
import requests
from bank_statement_pipeline.util.logger import logger

TOKEN_CACHE_PATH = "secret/token_cache.json"

class OutlookConnection:
    def __init__(self, client_id, tenant_id, username):
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.username = username
        self.token = None
        self.base_url = "https://graph.microsoft.com/v1.0"

    def connect(self):
        logger.info("🔐 Conectando à API Microsoft Graph via Device Code Flow")
        self.token = self._get_access_token()

    def disconnect(self):
        logger.info("🔌 Desconectado da API Microsoft Graph")

    def _get_access_token(self):
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        scopes = ["Mail.Read"]

        cache = msal.SerializableTokenCache()
        if os.path.exists(TOKEN_CACHE_PATH):
            with open(TOKEN_CACHE_PATH, "r") as f:
                cache.deserialize(f.read())

        app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=authority,
            token_cache=cache
        )

        accounts = app.get_accounts(username=self.username)
        result = app.acquire_token_silent(scopes, account=accounts[0]) if accounts else None

        if not result:
            logger.info("Iniciando fluxo de dispositivo para autenticação")
            flow = app.initiate_device_flow(scopes=scopes)
            if "user_code" not in flow:
                raise Exception("Erro ao iniciar device code flow")
            print(f"\n🔐 Vá até {flow['verification_uri']} e digite o código: {flow['user_code']}\n")
            result = app.acquire_token_by_device_flow(flow)

        if "access_token" not in result:
            raise Exception(f"Erro ao obter token: {result.get('error_description')}")

        if cache.has_state_changed:
            with open(TOKEN_CACHE_PATH, "w") as f:
                f.write(cache.serialize())

        logger.info("✅ Token obtido com sucesso")
        return result["access_token"]

    def get(self, endpoint, params=None):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/{endpoint}", headers=headers, params=params)
        response.raise_for_status()
        return response.json()
