
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("YOUR_MONGODB_URI_HERE"")
db = client["FitPulse"]

# Clear collections
db.current_health_logs.delete_many({})
db.prev_health_logs.delete_many({})

print("✅ Collections cleared.")
