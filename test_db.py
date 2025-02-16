from app.services.database import reviews_collection, wishlist_collection

# Test Insert
result = reviews_collection.insert_one({"test": "Hello MongoDB"})
print(f"Inserted ID: {result.inserted_id}")

# Test Find
data = reviews_collection.find_one({"test": "Hello MongoDB"})
print(f"Found Data: {data}")
