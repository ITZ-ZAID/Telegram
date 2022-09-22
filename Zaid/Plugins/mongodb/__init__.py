from pymongo import MongoClient
from config import MONGO_DB_URI

client = MongoClient(MONGO_DB_URI)
db = client["Melody"]
