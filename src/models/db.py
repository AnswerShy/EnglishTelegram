import os
from venv import logger
from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient
load_dotenv(find_dotenv())

try:
    url = os.getenv("MONGODB_URI")
    client = MongoClient(url, tls=True)
    db = client["english_teacher"]
except Exception as e:
    logger(f"Bot encountered an error: {e}")