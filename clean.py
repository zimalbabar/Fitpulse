
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb+srv://zimal_code:KS6W6g5r0vZslvw3@cluster0.nlm2hd4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["FitPulse"]

# Clear collections
db.current_health_logs.delete_many({})
db.prev_health_logs.delete_many({})

print("✅ Collections cleared.")