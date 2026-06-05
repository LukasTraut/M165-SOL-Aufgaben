import os
import random
from collections import deque
from pymongo import MongoClient
import pygame

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["jukebox_db"]
songs_col = db["songs"]

playlist: deque = deque()


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


def play_file(file_path: str, song_name: str):
    if not os.path.exists(file_path):
        print(f"Datei nicht gefunden: {file_path}")
        return

    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    print(f"Spiele: {song_name}")
    print("(Enter drücken zum Beenden)")

    input()
    pygame.mixer.music.stop()


def search_and_add():
    print("\nSong suchen")
    name = input("Name (leer = ignoriert): ").strip()
    artist = input("Interpret (leer = ignoriert): ").strip()
    album = input("Album (leer = ignoriert): ").strip()
    genre = input("Genre (leer = ignoriert): ").strip()

    results = search_songs(name, artist, album, genre)

    if not results:
        print("Keine Songs gefunden.")
        return

    print(f"\n{len(results)} Song(s) gefunden:")
    for i, s in enumerate(results, 1):
        info = f"  {i}. {s['name']} – {s['artist']}"
        if s.get("album"):
            info += f" | {s['album']}"
        if s.get("genre"):
            info += f" | {s['genre']}"
        print(info)

    try:
        idx = int(input("\nZur Playlist hinzufügen (Nummer, 0 = abbrechen): ")) - 1
        if idx == -1:
            return
        if 0 <= idx < len(results):
            song = results[idx]
            playlist.append(song)
            print(f"'{song['name']}' zur Playlist hinzugefügt.")
    except ValueError:
        print("Ungültige Eingabe.")


def play_next():
    if playlist:
        song = playlist.popleft()
        print(f"\nNächster Song aus Playlist: {song['name']} – {song['artist']}")
    else:
        all_songs = list(songs_col.find({}))
        if not all_songs:
            print("Keine Songs in der Datenbank.")
            return
        song = random.choice(all_songs)
        print(f"\nZufälliger Song: {song['name']} – {song['artist']}")

    file_path = song.get("file_path", "")
    if file_path:
        play_file(file_path, song["name"])
    else:
        print(f"[Kein Dateipfad gespeichert – Song: {song['name']}]")


def show_playlist():
    if not playlist:
        print("\nPlaylist ist leer.")
    else:
        print(f"\nPlaylist ({len(playlist)} Song(s)):")
        for i, s in enumerate(playlist, 1):
            print(f"  {i}. {s['name']} – {s['artist']}")


if __name__ == "__main__":
    while True:
        print("\n Jukebox Player ")
        print(f" Playlist: {len(playlist)} Song(s)")
        print(" 1. Song suchen & zur Playlist hinzufügen")
        print(" 2. Nächsten Song abspielen")
        print(" 3. Playlist anzeigen")
        print(" 0. Beenden")

        choice = input("Auswahl: ").strip()
        if choice == "1":
            search_and_add()
        elif choice == "2":
            play_next()
        elif choice == "3":
            show_playlist()
        elif choice == "0":
            break
        else:
            print("Ungültige Auswahl.")