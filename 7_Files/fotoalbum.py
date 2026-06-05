import os
import sys
from pymongo import MongoClient
import gridfs
 
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
 
client = MongoClient(MONGO_URI)
db = client["fotoalbum_db"]
fs = gridfs.GridFS(db)
 
 
def upload_photo(file_path: str, album: str):
    if not os.path.exists(file_path):
        print(f"Datei nicht gefunden: {file_path}")
        return
 
    filename = os.path.basename(file_path)
 
    with open(file_path, "rb") as f:
        file_id = fs.put(
            f,
            filename=filename,
            metadata={"album": album}
        )
 
    print(f"Bild '{filename}' in Album '{album}' gespeichert (ID: {file_id}).")
 
 
def download_album(album: str, output_dir: str = "."):
    os.makedirs(output_dir, exist_ok=True)
 
    files = db.fs.files.find({"metadata.album": album})
    file_list = list(files)
 
    if not file_list:
        print(f"Keine Bilder im Album '{album}' gefunden.")
        return
 
    print(f"{len(file_list)} Bild(er) im Album '{album}' gefunden:")
    for file_info in file_list:
        file_id = file_info["_id"]
        filename = file_info["filename"]
        output_path = os.path.join(output_dir, filename)
 
        grid_out = fs.get(file_id)
        with open(output_path, "wb") as f:
            f.write(grid_out.read())
 
        print(f"  Heruntergeladen: {output_path}")
 
 
def list_albums():
    albums = db.fs.files.distinct("metadata.album")
    if not albums:
        print("Keine Alben vorhanden.")
    else:
        print("Vorhandene Alben:")
        for album in albums:
            count = db.fs.files.count_documents({"metadata.album": album})
            print(f"  - {album} ({count} Bild(er))")
 
 
if __name__ == "__main__":
    while True:
        print("\n  Fotoalbum  ")
        print(" 1. Bild hochladen")
        print(" 2. Album herunterladen")
        print(" 3. Alle Alben anzeigen")
        print(" 0. Beenden")
 
        choice = input("Auswahl: ").strip()
 
        if choice == "1":
            path = input("Pfad zum Bild: ").strip()
            album = input("Albumname: ").strip()
            if album:
                upload_photo(path, album)
            else:
                print("Albumname darf nicht leer sein.")
 
        elif choice == "2":
            album = input("Albumname: ").strip()
            out = input("Ausgabeverzeichnis (leer = aktuelles Verzeichnis): ").strip() or "."
            download_album(album, out)
 
        elif choice == "3":
            list_albums()
 
        elif choice == "0":
            break
        else:
            print("Ungültige Auswahl.")
 