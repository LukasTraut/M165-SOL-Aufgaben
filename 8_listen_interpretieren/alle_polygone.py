import os

from pymongo import MongoClient
from PIL import Image, ImageDraw

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["sample_restaurants"]
neighborhoods = db["neighborhoods"]

docs = list(neighborhoods.find())
if not docs:
    print("Keine Dokumente in der Collection 'neighborhoods' gefunden.")
    exit(1)

print(f"{len(docs)} Neighborhoods gefunden.")

all_polygons = []
all_points_flat = []

for doc in docs:
    try:
        geo = doc["geometry"]
        geo_type = geo.get("type", "")

        if geo_type == "Polygon":
            rings = [geo["coordinates"][0]]
        elif geo_type == "MultiPolygon":
            rings = [poly[0] for poly in geo["coordinates"]]
        else:
            continue

        for ring in rings:
            points = [(c[0], c[1]) for c in ring]
            all_polygons.append(points)
            all_points_flat.extend(points)

    except (KeyError, IndexError, TypeError):
        continue

if not all_polygons:
    print("Keine gültigen Polygondaten gefunden.")
    exit(1)

print(f"{len(all_polygons)} Polygone werden gezeichnet.")

min_x = min(p[0] for p in all_points_flat)
max_x = max(p[0] for p in all_points_flat)
min_y = min(p[1] for p in all_points_flat)
max_y = max(p[1] for p in all_points_flat)

range_x = max_x - min_x or 1
range_y = max_y - min_y or 1

IMG_WIDTH = 900
IMG_HEIGHT = int(IMG_WIDTH * range_y / range_x)
IMG_HEIGHT = max(IMG_HEIGHT, 400)  
PADDING = 30

drawable_w = IMG_WIDTH - 2 * PADDING
drawable_h = IMG_HEIGHT - 2 * PADDING

def scale(px, py):
    x = PADDING + (px - min_x) / range_x * drawable_w
    y = PADDING + (max_y - py) / range_y * drawable_h
    return (x, y)

im = Image.new(mode="RGB", size=(IMG_WIDTH, IMG_HEIGHT), color=(15, 15, 30))
draw = ImageDraw.Draw(im)

PALETTE = [
    (70, 130, 200),   
    (100, 180, 120),  
    (200, 130, 60),   
    (180, 80, 120),   
    (80, 180, 180),   
    (200, 200, 70),   
    (150, 100, 200),  
]

for i, polygon in enumerate(all_polygons):
    scaled = [scale(p[0], p[1]) for p in polygon]

    if len(scaled) < 3:
        continue

    fill_color = PALETTE[i % len(PALETTE)]
    outline_color = tuple(min(255, c + 60) for c in fill_color)

    draw.polygon(scaled, fill=fill_color, outline=outline_color)

output_path = "aufgabe_8_3_output.png"
im.save(output_path)
im.show()
print(f"Bild gespeichert: {output_path}  ({IMG_WIDTH}x{IMG_HEIGHT} Pixel)")