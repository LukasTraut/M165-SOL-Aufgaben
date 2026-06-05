import os
import time
from datetime import datetime
from pymongo import MongoClient
import psutil
 
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MAX_LOGS = 10_000
 
client = MongoClient(MONGO_URI)
db = client["power_stats"]
collection = db["logs"]
 
 
class Power:
    
    def __init__(self, cpu: float = None, ram_total: int = None,
                 ram_used: int = None, timestamp: datetime = None):
        if cpu is None:
            self.cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            self.ram_total = ram.total
            self.ram_used = ram.used
            self.timestamp = datetime.utcnow()
        else:
            self.cpu = cpu
            self.ram_total = ram_total
            self.ram_used = ram_used
            self.timestamp = timestamp or datetime.utcnow()
 
    def to_dict(self) -> dict:
        return {
            "cpu": self.cpu,
            "ram_total": self.ram_total,
            "ram_used": self.ram_used,
            "timestamp": self.timestamp
        }
 
    def __repr__(self):
        ram_used_mb = self.ram_used / (1024 ** 2)
        ram_total_mb = self.ram_total / (1024 ** 2)
        return (f"[{self.timestamp.strftime('%H:%M:%S')}] "
                f"CPU: {self.cpu:.1f}% | "
                f"RAM: {ram_used_mb:.0f} MB / {ram_total_mb:.0f} MB")
 
 
def enforce_log_limit():
    count = collection.count_documents({})
    if count > MAX_LOGS:
        excess = count - MAX_LOGS
        oldest = list(
            collection.find({}, {"_id": 1})
            .sort("timestamp", 1)
            .limit(excess)
        )
        ids = [doc["_id"] for doc in oldest]
        collection.delete_many({"_id": {"$in": ids}})
        print(f"  [{excess} alte Einträge gelöscht]")
 
 
def run_logger():
    print("Power-Logger gestartet. Ctrl+C zum Beenden.")
    try:
        while True:
            power = Power()
            collection.insert_one(power.to_dict())
            enforce_log_limit()
            print(power)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nLogger beendet.")
 
 
if __name__ == "__main__":
    run_logger()
 