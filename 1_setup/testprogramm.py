import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

client = MongoClient(MONGO_URI)

info = client.server_info()
print("Verbindung erfolgreich!")
print(f"MongoDB Version: {info['version']}")

dbs = client.list_database_names()
print(f"Vorhandene Datenbanken: {dbs}") 