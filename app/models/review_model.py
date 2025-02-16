from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone

class ReviewModel(BaseModel):
    username: str = Field(..., description="User identifier (mandatory)")
    created_by: str = Field(..., description="Created by user or anonymous")
    source: str = Field(..., pattern="^(pusaka_chat|internal_system)$", description="Source of the review")
    review_title: str = Field(..., description="Title of the review")
    category: str = Field(..., pattern="^(product|service)$", description="Category of the review")
    price: int = Field(..., description="Price of the product/service (0 if free)")
    specifications: Optional[str] = Field(None, description="Product/service specifications")
    purchase_type: str = Field(..., pattern="^(online|offline)$", description="Type of purchase")
    store_name: Optional[str] = Field(None, description="Name of store/service provider")
    purchase_date: Optional[datetime] = Field(None, description="Purchase date (UTC format)")
    purchase_link: Optional[str] = Field(None, description="Purchase link or store address")
    review_content: str = Field(..., description="Content of the review")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    tags: List[str] = Field(default=[], description="List of tags/categories (array of strings)")
    image_urls: List[str] = Field(default=[], description="List of image URLs (array of strings)")

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Created timestamp (UTC)")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "alice_wonder",
                "created_by": "anonymous",
                "source": "pusaka_chat",
                "review_title": "Amazing Performance!",
                "category": "product",
                "price": 2500000,
                "specifications": "ram:8GB,storage:256GB",
                "purchase_type": "online",
                "store_name": "Shopee",
                "purchase_date": "2025-03-01T10:15:00",
                "purchase_link": "https://shopee.com/product/123",
                "review_content": "Super fast and battery life is great!",
                "rating": 5,
                "image_urls": ["https://img.com/iphone1.jpg", "https://img.com/iphone2.jpg"],
                "tags": ["smartphone", "apple"]
            }
        }
