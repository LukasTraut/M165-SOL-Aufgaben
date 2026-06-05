"""
Aufgabe 3 – CRUD Restaurant-Datenbank
Enthält alle Teilaufgaben 3.1 bis 3.7.
"""
import os
import re
from datetime import datetime
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["sample_restaurants"]
restaurants = db["restaurants"]

# 3.1: Alle Stadtbezirke ohne Duplikate
def aufgabe_3_1():
    print("  3.1: Alle Stadtbezirke (distinct)  ")
    boroughs = restaurants.distinct("borough")
    for b in sorted(boroughs):
        print(f" - {b}")


# 3.2: Top 3 Restaurants mit höchstem Durchschnitts-Rating
def aufgabe_3_2():
    print("\n  3.2: Top 3 Restaurants (Durchschnitts-Rating)  ")
    pipeline = [
        {"$unwind": "$grades"},
        {"$group": {
            "_id": "$name",
            "avg_score": {"$avg": "$grades.score"}
        }},
        {"$sort": {"avg_score": -1}},
        {"$limit": 3}
    ]
    results = list(restaurants.aggregate(pipeline))
    for i, r in enumerate(results, 1):
        print(f" {i}. {r['_id']} – Ø Score: {r['avg_score']:.2f}")


# 3.3: Nächstgelegenes Restaurant zu "Le Perigord"
def aufgabe_3_3():
    print("\n  3.3: Nächstgelegenes Restaurant zu 'Le Perigord'  ")

    le_perigord = restaurants.find_one({"name": "Le Perigord"})
    if not le_perigord:
        print("Restaurant 'Le Perigord' nicht gefunden.")
        return

    coords = le_perigord["address"]["coord"]
    print(f"Le Perigord Koordinaten: {coords}")

    pipeline = [
        {"$geoNear": {
            "near": {"type": "Point", "coordinates": coords},
            "distanceField": "dist",
            "spherical": True,
        }},
        {"$limit": 2}
    ]
    results = list(restaurants.aggregate(pipeline))
    nearest = results[1] if len(results) > 1 else None
    if nearest:
        print(f"Nächstes Restaurant: {nearest['name']}")
        print(f"Distanz: {nearest['dist']:.1f} Meter")
        print(f"Adresse: {nearest['address'].get('street', '')}, {nearest['address'].get('zipcode', '')}")
    else:
        print("Kein weiteres Restaurant gefunden.")


# 3.4, 3.5: Such Applikation und Bewertung hinzufügen
def search_restaurants(name: str = "", cuisine: str = "") -> list:
    """Sucht Restaurants nach Name und/oder Küche (optional, Teilstring)."""
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if cuisine:
        query["cuisine"] = {"$regex": cuisine, "$options": "i"}
    return list(restaurants.find(query, {"name": 1, "cuisine": 1, "borough": 1}))


def aufgabe_3_4_3_5():
    print("\n  3.4 / 3.5: Restaurant suchen & bewerten  ")

    name_input = input("Suchbegriff Name (leer = ignoriert): ").strip()
    cuisine_input = input("Suchbegriff Küche (leer = ignoriert): ").strip()

    results = search_restaurants(name_input, cuisine_input)

    if not results:
        print("Keine Restaurants gefunden.")
        return

    print(f"\n{len(results)} Restaurant(s) gefunden:")
    for i, r in enumerate(results, 1):
        print(f" {i}. {r['name']} – {r['cuisine']} ({r['borough']})")

    if len(results) > 1:
        try:
            choice = int(input("\nWelches Restaurant bewerten? (Nummer): ")) - 1
            if not 0 <= choice < len(results):
                print("Ungültige Auswahl.")
                return
        except ValueError:
            print("Ungültige Eingabe.")
            return
    else:
        choice = 0

    selected = results[choice]
    restaurant_id = selected["_id"]
    print(f"\nGewählt: {selected['name']}")

    try:
        score = int(input("Score (0–100): "))
    except ValueError:
        print("Ungültiger Score.")
        return

    new_grade = {
        "date": datetime.utcnow(),
        "grade": "A",
        "score": score
    }
    restaurants.update_one(
        {"_id": restaurant_id},
        {"$push": {"grades": new_grade}}
    )
    print(f"Bewertung ({score} Punkte) erfolgreich hinzugefügt.")


# 3.6: Restaurant hinzufügen
def validated_input(prompt: str, min_len: int = 2, exact_len: int = None) -> str:
    """Liest eine Eingabe mit Mindest- oder Exaktlängen-Validierung."""
    while True:
        value = input(prompt).strip()
        if exact_len is not None:
            if len(value) == exact_len:
                return value
            print(f"Eingabe muss genau {exact_len} Zeichen lang sein.")
        else:
            if len(value) >= min_len:
                return value
            print(f"Eingabe muss mindestens {min_len} Zeichen lang sein.")


def aufgabe_3_6():
    print("\n  3.6: Restaurant hinzufügen  ")

    name = validated_input("Name: ", min_len=2)
    borough = validated_input("Borough: ", min_len=2)
    cuisine = validated_input("Cuisine: ", min_len=2)
    building = input("Hausnummer (optional): ").strip()
    street = validated_input("Strasse: ", min_len=2)
    zipcode = validated_input("Postleitzahl: ", exact_len=5)

    new_restaurant = {
        "name": name,
        "borough": borough,
        "cuisine": cuisine,
        "address": {
            "building": building,
            "street": street,
            "zipcode": zipcode,
            "coord": []
        },
        "grades": [],
        "restaurant_id": str(datetime.utcnow().timestamp()).replace(".", "")
    }

    result = restaurants.insert_one(new_restaurant)
    print(f"Restaurant '{name}' erfolgreich hinzugefügt (ID: {result.inserted_id}).")


# 3.7: Restaurant löschen
def aufgabe_3_7():
    print("\n  3.7: Restaurant löschen  ")

    while True:
        name_input = input("Name oder Namenteil (min. 2 Zeichen): ").strip()
        if len(name_input) >= 2:
            break
        print("Bitte mindestens 2 Zeichen eingeben.")

    results = list(restaurants.find(
        {"name": {"$regex": name_input, "$options": "i"}},
        {"name": 1, "borough": 1}
    ))

    if not results:
        print("Keine Restaurants gefunden.")
        return

    print(f"\n{len(results)} Restaurant(s) gefunden:")
    for r in results:
        print(f" - {r['name']} ({r['borough']})")

    confirm = input(f"\nMöchten Sie diese {len(results)} Restaurant(s) wirklich löschen? (ja/nein): ").strip().lower()
    if confirm == "ja":
        ids = [r["_id"] for r in results]
        delete_result = restaurants.delete_many({"_id": {"$in": ids}})
        print(f"{delete_result.deleted_count} Restaurant(s) gelöscht.")
    else:
        print("Löschvorgang abgebrochen.")


if __name__ == "__main__":
    menu = {
        "1": ("3.1 – Alle Stadtbezirke", aufgabe_3_1),
        "2": ("3.2 – Top 3 Restaurants", aufgabe_3_2),
        "3": ("3.3 – Nächstes Restaurant zu Le Perigord", aufgabe_3_3),
        "4": ("3.4/3.5 – Suchen & Bewerten", aufgabe_3_4_3_5),
        "5": ("3.6 – Restaurant hinzufügen", aufgabe_3_6),
        "6": ("3.7 – Restaurant löschen", aufgabe_3_7),
    }

    while True:
        print("\n  Aufgabe 3: Restaurant-Datenbank  ")
        for key, (label, _) in menu.items():
            print(f" {key}. {label}")
        print(" 0. Beenden")

        choice = input("Auswahl: ").strip()
        if choice == "0":
            break
        elif choice in menu:
            menu[choice][1]()
        else:
            print("Ungültige Auswahl.") 