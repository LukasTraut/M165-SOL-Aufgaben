import os
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
 
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
 
 
# Aufgabe 6.1: Dao_room
class Room:
    def __init__(self, name: str, capacity: int, room_id: str = None):
        self.name = name
        self.capacity = capacity
        self.id = room_id
 
    def to_dict(self) -> dict:
        return {"name": self.name, "capacity": self.capacity}
 
    def __repr__(self):
        return f"Room(id={self.id}, name={self.name}, capacity={self.capacity})"
 
 
class Dao_room:
    def __init__(self):
        db = client["rooms_db"]
        self.collection = db["rooms"]
 
    def insert(self, room: Room) -> str:
        result = self.collection.insert_one(room.to_dict())
        return str(result.inserted_id)
 
    def get_all(self) -> list[Room]:
        docs = self.collection.find({})
        return [Room(d["name"], d["capacity"], str(d["_id"])) for d in docs]
 
    def get_by_id(self, room_id: str) -> Room | None:
        doc = self.collection.find_one({"_id": ObjectId(room_id)})
        if doc:
            return Room(doc["name"], doc["capacity"], str(doc["_id"]))
        return None
 
    def update(self, room_id: str, name: str = None, capacity: int = None) -> bool:
        updates = {}
        if name is not None:
            updates["name"] = name
        if capacity is not None:
            updates["capacity"] = capacity
        if not updates:
            return False
        result = self.collection.update_one(
            {"_id": ObjectId(room_id)},
            {"$set": updates}
        )
        return result.modified_count > 0
 
    def delete(self, room_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(room_id)})
        return result.deleted_count > 0
 
 
# Aufgabe 6.2: Joke Klasse & Dao_joke
class Joke:
    def __init__(self, text: str, category: list[str], author: str, joke_id: str = None):
        self.text = text
        self.category = category 
        self.id = joke_id
 
    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "category": self.category,
            "author": self.author
        }
 
    def __repr__(self):
        cats = ", ".join(self.category)
        return f'Joke(id={self.id}, author={self.author}, categories=[{cats}])\n  "{self.text}"'
 
 
class Dao_joke:
    def __init__(self):
        db = client["jokes_db"]
        self.collection = db["jokes"]
 
    def insert(self, joke: Joke) -> str:
        result = self.collection.insert_one(joke.to_dict())
        return str(result.inserted_id)
 
    def get_category(self, category: str) -> list[Joke]:
        docs = self.collection.find({"category": category})
        return [
            Joke(d["text"], d["category"], d["author"], str(d["_id"]))
            for d in docs
        ]
 
    def delete(self, joke_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(joke_id)})
        return result.deleted_count > 0
 
 
if __name__ == "__main__":
    print("  6.1: Dao_room Demo  ")
    dao_room = Dao_room()
 
    r1 = Room("Sitzungszimmer A", 10)
    r2 = Room("Serverraum", 3)
    id1 = dao_room.insert(r1)
    id2 = dao_room.insert(r2)
    print(f"Eingefügt: {id1}, {id2}")
 
    
    dao_room.update(id1, capacity=12)
    print(f"Nach Update: {dao_room.get_by_id(id1)}")
 
   
    dao_room.delete(id2)
    print(f"Nach Delete: {[str(r) for r in dao_room.get_all()]}")
 
    print("\n  6.2: Dao_joke Demo  ")
    dao_joke = Dao_joke()
 
    j1 = Joke("Warum können Geister schlecht lügen? Weil man durch sie hindurchsehen kann.",
              ["Halloween", "Wortspiel"], "Max")
    j2 = Joke("Was macht ein Krokodil, wenn es dir begegnet? Es beisst dich!",
              ["Tiere"], "Lisa")
    j3 = Joke("Was sagt ein Clown zum anderen? Ist dir das ernst?",
              ["Wortspiel", "Clown"], "Tom")
 
    id_j1 = dao_joke.insert(j1)
    id_j2 = dao_joke.insert(j2)
    id_j3 = dao_joke.insert(j3)
    print(f"Eingefügt: {id_j1}, {id_j2}, {id_j3}")
 
    print("\nKategorie 'Wortspiel':")
    for joke in dao_joke.get_category("Wortspiel"):
        print(f"  {joke}")
 
    dao_joke.delete(id_j2)
    print(f"\nNach Löschen von j2: {len(dao_joke.get_category('Tiere'))} Tier-Joke(s) übrig.")