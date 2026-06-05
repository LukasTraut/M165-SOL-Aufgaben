import os
from pymongo import MongoClient
from PIL import Image, ImageDraw 

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["sample_restaurants"]
neighborhoods = db["neighborhoods"]

doc = neighborhoods.find_one()
if doc is None:
    print("Keine Dokumente in der Collection 'neighborhoods' gefunden.")
    exit(1)

print(f"Zeichne Polygon für: {doc.get('name', 'Unbekannt')}")

coords = doc["geometry"]["coordinates"][0]

raw_points = [(c[0], c[1]) for c in coords]

IMG_SIZE = 600
PADDING = 40

min_x = min(p[0] for p in raw_points)
max_x = max(p[0] for p in raw_points)
min_y = min(p[1] for p in raw_points)
max_y = max(p[1] for p in raw_points)

range_x = max_x - min_x or 1
range_y = max_y - min_y or 1

drawable_size = IMG_SIZE - 2 * PADDING

def scale(px, py):
    x = PADDING + (px - min_x) / range_x * drawable_size
    y = PADDING + (max_y - py) / range_y * drawable_size
    return (x, y)

scaled_points = [scale(p[0], p[1]) for p in raw_points]

im = Image.new(mode="RGB", size=(IMG_SIZE, IMG_SIZE), color=(20, 20, 40))
draw = ImageDraw.Draw(im)

draw.polygon(scaled_points, fill=(60, 120, 200), outline=(0, 220, 255))

name = doc.get("name", "Neighborhood")
print(f"Polygon mit {len(scaled_points)} Punkten gezeichnet.")

output_path = "aufgabe_8_2_output.png"
im.save(output_path)
im.show()
print(f"Bild gespeichert: {output_path}")