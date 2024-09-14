import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
ADSPOWER_ID1 = os.environ.get("ADSPOWER_ID1")
ADSPOWER_ID2 = os.environ.get("ADSPOWER_ID2")
ADSPOWER_NAME1 = os.environ.get("ADSPOWER_NAME1")
ADSPOWER_NAME2 = os.environ.get("ADSPOWER_NAME2")

proxy_list = [
    {
        "PROXY_HOST": "",
        "PROXY_PORT": "",
        "PROXY_PSW": "",
        "PROXY_LOGIN": "",
    },
    {
        "PROXY_HOST": "",
        "PROXY_PORT": "",
        "PROXY_PSW": "",
        "PROXY_LOGIN": "",
    },
]
