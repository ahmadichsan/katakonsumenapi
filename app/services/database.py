import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ambil konfigurasi dari .env
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Buat koneksi MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Koleksi (Collections)
reviews_collection = db["reviews"]
wishlist_collection = db["wishlist"]

# Cek koneksi (Opsional, bisa untuk debug)
try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")
