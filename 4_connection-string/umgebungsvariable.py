import os
from pymongo import MongoClient
 
mongo_uri = os.environ.get("MONGO_URI")
 
if not mongo_uri:
    print("FEHLER: Umgebungsvariable MONGO_URI ist nicht gesetzt.")
    print("Bitte setzen Sie die Variable und starten das Programm erneut.")
    exit(1)
 
print(f"Verbinde mit: {mongo_uri[:30]}...") 
client = MongoClient(mongo_uri)
 
try:
    info = client.server_info()
    print(f"Verbindung erfolgreich! MongoDB Version: {info['version']}")
    dbs = client.list_database_names()
    print(f"Verfügbare Datenbanken: {dbs}")
except Exception as e:
    print(f"Verbindung fehlgeschlagen: {e}")