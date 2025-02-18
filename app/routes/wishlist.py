from fastapi import APIRouter, HTTPException, Request
from app.models.wishlist_model import WishlistModel
from app.services.database import wishlist_collection
from datetime import datetime, timezone
from app.utils.utils import sql_like_search, trim_value

router = APIRouter()

@router.post("/api/wishlist", response_description="Create a new wishlist")
async def create_wishlist(wishlist: WishlistModel):
    wishlist_data = wishlist.model_dump()

    allowed_fields = {"username", "wishlist_title"}
    filtered_data = {
        k: trim_value(v) 
        for k, v in wishlist_data.items() 
        if k in allowed_fields
    }

    # Tambahkan created_at otomatis
    filtered_data["created_at"] = datetime.now(timezone.utc)

    # Simpan ke MongoDB
    try:
        result = wishlist_collection.insert_one(filtered_data)
        return {"status": "success", "message": "Wishlist created successfully", "wishlist_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving wishlist: {e}")

@router.post("/api/wishlist/search", response_description="Get wishlist by username and title with total data")
async def get_wishlist(request: Request):
    body = await request.json()

    # Validate required username
    if "username" not in body or not body["username"]:
        raise HTTPException(status_code=400, detail="Username is required")

    query = {"username": sql_like_search(body["username"])}

    if "wishlist_title" in body and body["wishlist_title"]:
        query["wishlist_title"] = sql_like_search(body["wishlist_title"])

    # Total data matching (tanpa limit)
    total_data = wishlist_collection.count_documents(query)

    # Query Execution (with limit)
    limit = body.get("limit", 30)
    wishlists = list(wishlist_collection.find(query).limit(limit))
    returned_data = len(wishlists)

    for wishlist in wishlists:
        wishlist["_id"] = str(wishlist["_id"])

    return {
        "status": "success",
        "total_data": total_data,
        "returned_data": returned_data,
        "wishlists": wishlists
    }

@router.post("/api/wishlist/delete-by-username-and-title", response_description="Delete wishlist by username and title")
async def delete_wishlist_by_username_and_title(request: Request):
    body = await request.json()
    username = body.get("username")
    title = body.get("wishlist_title")

    if not username or not title:
        raise HTTPException(status_code=400, detail="Username and Wishlist Title are required")

    query = {
        "username": username,
        "wishlist_title": {"$regex": f"^{title}$", "$options": "i"}  # Exact match, case-insensitive
    }

    result = wishlist_collection.delete_one(query)

    if result.deleted_count == 1:
        return {"status": "success", "message": "Wishlist deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Wishlist not found")

@router.post("/api/wishlist/delete-all-by-username", response_description="Delete all wishlists by username")
async def delete_all_wishlist_by_username(request: Request):
    body = await request.json()
    username = body.get("username")

    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    result = wishlist_collection.delete_many({"username": username})

    return {
        "status": "success",
        "deleted_wishlists": result.deleted_count,
        "message": "All wishlists deleted successfully"
    }
