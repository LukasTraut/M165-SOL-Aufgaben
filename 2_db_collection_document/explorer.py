import os
import msvcrt 
from pymongo import MongoClient
from bson import ObjectId

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)


def wait_for_key():
    print("\nPress any button to return")
    try:
        msvcrt.getch()
    except Exception:
        input()


def show_document_content(doc: dict):
    for key, value in doc.items():
        if key != "_id":
            print(f"{key}: {value}")


def run():
    while True:
        db_names = [
            name for name in client.list_database_names()
            if name not in ("admin", "local", "config")
        ]

        if not db_names:
            print("No Database")
            wait_for_key()
            continue

        print("\nDatabases")
        for name in db_names:
            print(f" - {name}")

        db_input = input("\nSelect Database: ").strip()
        if db_input not in db_names:
            print(f"Database '{db_input}' not found. Please try again.")
            continue

        db = client[db_input]

        while True:
            col_names = db.list_collection_names()

            print(f"\n{db_input}")
            if not col_names:
                print("No Collection")
                wait_for_key()
                break

            print("Collections")
            for name in col_names:
                print(f" - {name}")

            col_input = input("\nSelect Collection: ").strip()
            if col_input not in col_names:
                print(f"Collection '{col_input}' not found. Please try again.")
                continue

            collection = db[col_input]

            while True:
                docs = list(collection.find({}, {"_id": 1}))

                print(f"\n{db_input}.{col_input}")
                if not docs:
                    print("No Document")
                    wait_for_key()
                    break

                print("Documents")
                for doc in docs:
                    print(f" - {doc['_id']}")

                doc_input = input("\nSelect Document: ").strip()

                try:
                    oid = ObjectId(doc_input)
                except Exception:
                    print(f"Document '{doc_input}' not found. Please try again.")
                    continue

                selected = collection.find_one({"_id": oid})
                if selected is None:
                    print(f"Document '{doc_input}' not found. Please try again.")
                    continue

                print(f"\n{db_input}.{col_input}.{doc_input}")
                show_document_content(selected)
                wait_for_key()
                break  

            break 


if __name__ == "__main__":
    run()