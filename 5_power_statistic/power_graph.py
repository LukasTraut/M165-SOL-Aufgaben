import os
from datetime import datetime
from pymongo import MongoClient
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

client = MongoClient(MONGO_URI)
db = client["power_stats"]
collection = db["logs"]


def load_data(limit: int = 200) -> tuple:
    """Lädt die neuesten Logs aus MongoDB."""
    docs = list(
        collection.find({})
        .sort("timestamp", -1)
        .limit(limit)
    )
    docs.reverse()

    timestamps = [d["timestamp"] for d in docs]
    cpu_values = [d["cpu"] for d in docs]
    ram_used = [d["ram_used"] / (1024 ** 2) for d in docs]   # in MB
    ram_total = [d["ram_total"] / (1024 ** 2) for d in docs]  # in MB

    return timestamps, cpu_values, ram_used, ram_total


def show_graph():
    timestamps, cpu_values, ram_used, ram_total = load_data()

    if not timestamps:
        print("Keine Daten in der Datenbank gefunden.")
        print("Bitte zuerst aufgabe_5_3.py ausführen, um Daten zu sammeln.")
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    fig.suptitle("Power Statistics", fontsize=14, fontweight="bold")

    ax1.plot(timestamps, cpu_values, color="steelblue", linewidth=1.5, label="CPU %")
    ax1.fill_between(timestamps, cpu_values, alpha=0.2, color="steelblue")
    ax1.set_ylabel("CPU (%)")
    ax1.set_ylim(0, 100)
    ax1.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)

    ax2.plot(timestamps, ram_used, color="tomato", linewidth=1.5, label="RAM verwendet (MB)")
    ax2.plot(timestamps, ram_total, color="gray", linewidth=1, linestyle="--", label="RAM total (MB)")
    ax2.fill_between(timestamps, ram_used, alpha=0.2, color="tomato")
    ax2.set_ylabel("RAM (MB)")
    ax2.set_xlabel("Zeit")
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    show_graph()