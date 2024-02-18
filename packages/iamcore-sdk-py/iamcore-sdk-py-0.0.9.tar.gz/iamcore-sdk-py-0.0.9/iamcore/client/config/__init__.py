import os
from dotenv import load_dotenv


class BaseConfig(object):
    IAMCORE_URL: str
    IAMCORE_ISSUER_URL: str
    SYSTEM_BACKEND_CLIENT_ID: str

    def set_iamcore_config(self, iamcore_url: str, iamcore_issuer_url: str, client_id: str):
        self.IAMCORE_URL = iamcore_url
        self.IAMCORE_ISSUER_URL = iamcore_issuer_url
        self.SYSTEM_BACKEND_CLIENT_ID = client_id

    @classmethod
    def __init__(self):
        load_dotenv()
        self.IAMCORE_URL: str = os.getenv("IAMCORE_URL")
        self.IAMCORE_ISSUER_URL: str = os.environ.get('IAMCORE_ISSUER_URL')
        self.SYSTEM_BACKEND_CLIENT_ID: str = os.environ.get('SYSTEM_BACKEND_CLIENT_ID')


config = BaseConfig()
