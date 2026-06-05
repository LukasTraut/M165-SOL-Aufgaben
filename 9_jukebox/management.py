import os
from pymongo import MongoClient
from bson import ObjectId

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["jukebox_db"]
songs_col = db["songs"]


class Song:
    def __init__(self, name: str, artist: str, album: str = None,
                 genre: str = None, year: int = None, song_id: str = None):
        self.name = name
        self.artist = artist
        self.album = album
        self.genre = genre
        self.year = year
        self.id = song_id

    def to_dict(self) -> dict:
        doc = {"name": self.name, "artist": self.artist}
        if self.album:
            doc["album"] = self.album
        if self.genre:
            doc["genre"] = self.genre
        if self.year:
            doc["year"] = self.year
        return doc

    def __repr__(self):
        parts = [f"'{self.name}' von {self.artist}"]
        if self.album:
            parts.append(f"Album: {self.album}")
        if self.genre:
            parts.append(f"Genre: {self.genre}")
        if self.year:
            parts.append(f"Jahr: {self.year}")
        return " | ".join(parts)


def search_songs(name="", artist="", album="", genre="") -> list[dict]:
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if artist:
        query["artist"] = {"$regex": artist, "$options": "i"}
    if album:
        query["album"] = {"$regex": album, "$options": "i"}
    if genre:
        query["genre"] = {"$regex": genre, "$options": "i"}
    return list(songs_col.find(query))


def select_song(prompt="Song auswählen") -> dict | None:
    name = input("Suchbegriff Name: ").strip()
    artist = input("Suchbegriff Interpret: ").strip()
    results = search_songs(name=name, artist=artist)

    if not results:
        print("Keine Songs gefunden.")
        return None

    print(f"\n{len(results)} Song(s) gefunden:")
    for i, s in enumerate(results, 1):
        print(f"  {i}. {s['name']} – {s['artist']}")

    try:
        idx = int(input(f"{prompt} (Nummer): ")) - 1
        if 0 <= idx < len(results):
            return results[idx]
    except ValueError:
        pass
    print("Ungültige Auswahl.")
    return None


def add_song():
    print("\n  Song hinzufügen  ")
    name = input("Name (Pflicht): ").strip()
    artist = input("Interpret (Pflicht): ").strip()
    if not name or not artist:
        print("Name und Interpret sind Pflichtfelder.")
        return
    album = input("Album (optional): ").strip() or None
    genre = input("Genre (optional): ").strip() or None
    year_str = input("Erscheinungsjahr (optional): ").strip()
    year = int(year_str) if year_str.isdigit() else None

    song = Song(name, artist, album, genre, year)
    result = songs_col.insert_one(song.to_dict())
    print(f"Song '{name}' gespeichert (ID: {result.inserted_id}).")


def edit_song():
    print("\n  Song bearbeiten  ")
    song = select_song("Song zum Bearbeiten")
    if not song:
        return

    print(f"\nAktuell: {Song(song['name'], song['artist'], song.get('album'), song.get('genre'), song.get('year'))}")
    print("(Leer lassen = nicht ändern)")

    updates = {}
    for field, label in [("name", "Name"), ("artist", "Interpret"),
                          ("album", "Album"), ("genre", "Genre"), ("year", "Jahr")]:
        val = input(f"{label}: ").strip()
        if val:
            updates[field] = int(val) if field == "year" and val.isdigit() else val

    if updates:
        songs_col.update_one({"_id": song["_id"]}, {"$set": updates})
        print("Song erfolgreich aktualisiert.")
    else:
        print("Keine Änderungen vorgenommen.")


def delete_song():
    print("\n  Song löschen  ")
    song = select_song(" Song zum Löschen ")
    if not song:
        return

    confirm = input(f"'{song['name']}' wirklich löschen? (ja/nein): ").strip().lower()
    if confirm == "ja":
        songs_col.delete_one({"_id": song["_id"]})
        print("Song gelöscht.")
    else:
        print("Abgebrochen.")


if __name__ == "__main__":
    while True:
        print("\nJukebox Management")
        print(" 1. Song hinzufügen")
        print(" 2. Song bearbeiten")
        print(" 3. Song löschen")
        print(" 0. Beenden")

        choice = input(" Auswahl: ").strip()
        if choice == "1":
            add_song()
        elif choice == "2":
            edit_song()
        elif choice == "3":
            delete_song()
        elif choice == "0":
            break
        else:
            print("Ungültige Auswahl.") 