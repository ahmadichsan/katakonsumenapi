from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request
from app.models.review_model import ReviewModel
from app.services.database import reviews_collection
from datetime import datetime, timezone
from app.services.supabase_service import delete_from_supabase, is_image_url, download_image, upload_to_supabase
from app.utils.utils import array_like_search, parse_comma_separated, sql_like_search, trim_value

router = APIRouter()

@router.post("/api/reviews", response_description="Create a new review")
async def create_review(request: Request):
    # Ambil payload mentah
    raw_body = await request.json()

    # CHANGED: Konversi 'tags' & 'image_urls' dari string ke list jika perlu, dengan trim
    if "tags" in raw_body:
        if isinstance(raw_body["tags"], str):
            raw_body["tags"] = [tag.strip() for tag in parse_comma_separated(raw_body["tags"])]
        else:
            raw_body["tags"] = trim_value(raw_body["tags"])

    if "image_urls" in raw_body:
        if isinstance(raw_body["image_urls"], str):
            raw_body["image_urls"] = [url.strip() for url in parse_comma_separated(raw_body["image_urls"])]
        else:
            raw_body["image_urls"] = trim_value(raw_body["image_urls"])

    string_fields = [
        "username", "created_by", "review_title", "category",
        "specifications", "purchase_type", "store_name",
        "purchase_link", "review_content"
    ]

    for field in string_fields:
        if field in raw_body and isinstance(raw_body[field], str):
            raw_body[field] = raw_body[field].strip()

    # Validasi dengan Pydantic setelah konversi
    review = ReviewModel(**raw_body)
    review_data = review.model_dump()
    
    uploaded_image_urls = []

    for image_url in review_data.get("image_urls", []):
        # Cek apakah URL adalah image/*
        if not is_image_url(image_url):
            print(f"Skipped non-image URL: {image_url}")
            continue

        image_bytes = download_image(image_url)
        if not image_bytes:
            print(f"Skipping {image_url} due to download failure or invalid content.")
            continue

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

@router.post("/api/reviews/search", response_description="Search reviews with total data")
async def search_reviews(request: Request):
    body = await request.json()
    query = {}

    # String Fields: Case-insensitive partial matching
    string_fields = [
        "username", "created_by", "review_title", "category",
        "specifications", "purchase_type", "store_name",
        "purchase_link", "review_content"
    ]

    for field in string_fields:
        if field in body and body[field]:
            query[field] = sql_like_search(body[field])

    # Array Matching (Tags)
    if "tags" in body and body["tags"]:
        tags = [tag.strip() for tag in body["tags"].split(",")]
        query.update(array_like_search(tags))


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

    # Total data matching (tanpa limit)
    total_data = reviews_collection.count_documents(query)

    # Query Execution (with limit)
    limit = body.get("limit", 30)
    results = list(reviews_collection.find(query).limit(limit))
    returned_data = len(results)

    for review in results:
        review["_id"] = str(review["_id"])

    return {
        "status": "success",
        "total_data": total_data,
        "returned_data": returned_data,
        "reviews": results
    }

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

@router.post("/api/reviews/get-by-username", response_description="Get all reviews by username")
async def get_reviews_by_username(request: Request):
    body = await request.json()
    username = body.get("username")

    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    query = {"username": username}
    reviews = list(reviews_collection.find(query))
    
    for review in reviews:
        review["_id"] = str(review["_id"])
    
    return {
        "status": "success",
        "total_reviews": len(reviews),
        "reviews": reviews
    }

@router.post("/api/reviews/delete-by-id", response_description="Delete review by review ID")
async def delete_review_by_id(request: Request):
    body = await request.json()
    review_id = body.get("review_id")

    if not review_id:
        raise HTTPException(status_code=400, detail="Review ID is required")

    # Cari review dulu
    review = reviews_collection.find_one({"_id": ObjectId(review_id)})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Hapus gambar dari Supabase
    for image_url in review.get("image_urls", []):
        delete_from_supabase(image_url)

    # Hapus review dari MongoDB
    result = reviews_collection.delete_one({"_id": ObjectId(review_id)})
    
    if result.deleted_count == 1:
        return {"status": "success", "message": "Review deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete review")

@router.post("/api/reviews/delete-all-by-username", response_description="Delete all reviews by username")
async def delete_all_reviews_by_username(request: Request):
    body = await request.json()
    username = body.get("username")

    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    # Cari semua review
    reviews = list(reviews_collection.find({"username": username}))
    
    # Hapus semua gambar di Supabase
    for review in reviews:
        for image_url in review.get("image_urls", []):
            delete_from_supabase(image_url)

    # Hapus semua review dari MongoDB
    result = reviews_collection.delete_many({"username": username})

    return {
        "status": "success",
        "deleted_reviews": result.deleted_count,
        "message": "All reviews deleted successfully"
    }
