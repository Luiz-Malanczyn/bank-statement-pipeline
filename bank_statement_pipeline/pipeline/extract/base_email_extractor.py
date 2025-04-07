from abc import ABC, abstractmethod

class BaseEmailExtractor(ABC):
    @abstractmethod
    def connect(self):
        """Estabelece conexão com o servidor de email."""
        pass

    @abstractmethod
    def fetch_attachments(self):
        """Busca e retorna os anexos dos emails de interesse."""
        pass

    @abstractmethod
    def disconnect(self):
        """Finaliza a conexão."""
        pass

    def run(self):
        """Template method para orquestrar o processo."""
        self.connect()
        try:
            attachments = self.fetch_attachments()
        finally:
            self.disconnect()
        return attachments
