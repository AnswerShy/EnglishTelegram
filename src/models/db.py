import os
from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient
load_dotenv(find_dotenv())

url = os.getenv("MONGODB_URI")
# print (f"MongoDB URL: {url}")
client = MongoClient(url, tls=True)
db = client["english_teacher"]
