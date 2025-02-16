from bson import ObjectId
from typing import List
from fastapi import APIRouter, HTTPException, Request
from app.models.review_model import ReviewModel
from app.services.database import reviews_collection
from datetime import datetime, timezone
import re
from app.services.supabase_service import is_image_url, download_image, upload_to_supabase

router = APIRouter()

def parse_comma_separated(value: str) -> List[str]:
    """Convert comma-separated string to list of strings."""
    return value.split(",") if value else []

@router.post("/api/reviews", response_description="Create a new review")
async def create_review(request: Request):
    # Ambil payload mentah
    raw_body = await request.json()

    # Konversi 'tags' & 'image_urls' dari string ke list jika perlu
    if "tags" in raw_body and isinstance(raw_body["tags"], str):
        raw_body["tags"] = parse_comma_separated(raw_body["tags"])

    if "image_urls" in raw_body and isinstance(raw_body["image_urls"], str):
        raw_body["image_urls"] = parse_comma_separated(raw_body["image_urls"])

    # Validasi dengan Pydantic setelah konversi
    review = ReviewModel(**raw_body)
    review_data = review.model_dump()
    
    uploaded_image_urls = []

    for image_url in review_data.get("image_urls", []):
        image_bytes = download_image(image_url)
        if not image_bytes:
            print(f"Skipping {image_url} due to download failure or invalid content.")
            continue  # Skip if not downloadable or not image/*

        blob_url = upload_to_supabase(review_data["username"], image_bytes)
        if blob_url:
            uploaded_image_urls.append(blob_url)
        else:
            print(f"Skipping {image_url} due to upload failure.")

    # Simpan hanya URL hasil upload yang berhasil
    review_data["image_urls"] = uploaded_image_urls

    # Tambahkan created_at otomatis
    review_data["created_at"] = datetime.now(timezone.utc)

    # Simpan ke MongoDB
    try:
        result = reviews_collection.insert_one(review_data)
        return {"status": "success", "message": "Review created successfully", "review_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving review: {e}")

def sql_like_search(value: str) -> dict:
    """SQL-like substring search (case-insensitive)."""
    escaped_value = re.escape(value)  # Escape regex special chars
    pattern = f"(?=.*{escaped_value})"  # Positive lookahead pattern
    return {"$regex": pattern, "$options": "i"}

@router.post("/api/reviews/search", response_description="Search reviews")
async def search_reviews(request: Request):
    body = await request.json()  # Ambil filter dari body payload
    query = {}

    # String Fields: SQL-like Search
    string_fields = [
        "username", "created_by", "review_title", "category",
        "specifications", "purchase_type", "store_name",
        "purchase_link", "review_content"
    ]

    for field in string_fields:
        if field in body and body[field]:
            query[field] = sql_like_search(body[field])

    # Range Filters
    if "price_min" in body or "price_max" in body:
        query["price"] = {}
        if "price_min" in body:
            query["price"]["$gte"] = body["price_min"]
        if "price_max" in body:
            query["price"]["$lte"] = body["price_max"]

    if "rating_min" in body or "rating_max" in body:
        query["rating"] = {}
        if "rating_min" in body:
            query["rating"]["$gte"] = body["rating_min"]
        if "rating_max" in body:
            query["rating"]["$lte"] = body["rating_max"]

    # Date Range Filters
    from datetime import datetime
    if "purchase_date_start" in body and "purchase_date_end" in body:
        query["purchase_date"] = {
            "$gte": datetime.fromisoformat(body["purchase_date_start"]),
            "$lte": datetime.fromisoformat(body["purchase_date_end"])
        }

    if "created_at_start" in body and "created_at_end" in body:
        query["created_at"] = {
            "$gte": datetime.fromisoformat(body["created_at_start"]),
            "$lte": datetime.fromisoformat(body["created_at_end"])
        }

    # Array Matching
    if "tags" in body and body["tags"]:
        query["tags"] = {"$in": body["tags"].split(",")}
    if "image_urls" in body and body["image_urls"]:
        query["image_urls"] = {"$in": body["image_urls"].split(",")}

    # Query Execution
    limit = body.get("limit", 10)
    results = list(reviews_collection.find(query).limit(limit))

    for review in results:
        review["_id"] = str(review["_id"])  # Convert ObjectId to string

    return {"status": "success", "reviews": results}

@router.post("/api/reviews/detail", response_description="Get review detail by review_id")
async def get_review_detail(request: Request):
    body = await request.json()  # Terima filter dari body

    if "review_id" not in body or not body["review_id"]:
        raise HTTPException(status_code=400, detail="Review ID is required")

    try:
        review = reviews_collection.find_one({"_id": ObjectId(body["review_id"])})
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        review["_id"] = str(review["_id"])
        return {"status": "success", "review": review}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving review: {e}")

