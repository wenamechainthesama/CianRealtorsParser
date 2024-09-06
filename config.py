import os
from dotenv import load_dotenv

load_dotenv() 

DATABASE_URL = os.environ.get("DATABASE_URL")
ADSPOWER_ID = os.environ.get("ADSPOWER_ID")
ADSPOWER_NAME = os.environ.get("ADSPOWER_NAME")
