from fastapi import APIRouter, HTTPException, Request
from app.models.wishlist_model import WishlistModel
from app.services.database import wishlist_collection
from datetime import datetime, timezone
import re

router = APIRouter()

@router.post("/api/wishlist", response_description="Create a new wishlist")
async def create_wishlist(wishlist: WishlistModel):
    wishlist_data = wishlist.model_dump()

    # Hanya proses field yang diharapkan (abaikan yang lain)
    allowed_fields = {"username", "wishlist_title"}
    filtered_data = {k: v for k, v in wishlist_data.items() if k in allowed_fields}

    # Tambahkan created_at otomatis
    filtered_data["created_at"] = datetime.now(timezone.utc)

    # Simpan ke MongoDB
    try:
        result = wishlist_collection.insert_one(filtered_data)
        return {"status": "success", "message": "Wishlist created successfully", "wishlist_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving wishlist: {e}")


def sql_like_search(value: str) -> dict:
    """SQL-like substring search (case-insensitive)."""
    escaped_value = re.escape(value)
    pattern = f"(?=.*{escaped_value})"
    return {"$regex": pattern, "$options": "i"}

@router.post("/api/wishlist/search", response_description="Get wishlist by username and title")
async def get_wishlist(request: Request):
    body = await request.json()

    # Validasi: username harus mandatory
    if "username" not in body or not body["username"]:
        raise HTTPException(status_code=400, detail="Username is required")

    query = {"username": body["username"]}  # Username wajib

    # Filter by Wishlist Title (LIKE)
    if "wishlist_title" in body and body["wishlist_title"]:
        query["wishlist_title"] = sql_like_search(body["wishlist_title"])

    try:
        wishlists = list(wishlist_collection.find(query))
        for wishlist in wishlists:
            wishlist["_id"] = str(wishlist["_id"])
        return {"status": "success", "wishlists": wishlists}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving wishlist: {e}")
