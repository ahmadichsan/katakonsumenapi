from pydantic import BaseModel, Field
from datetime import datetime, timezone

class WishlistModel(BaseModel):
    username: str = Field(..., description="User identifier (mandatory)")
    wishlist_title: str = Field(..., description="Title of wishlist item (product/service)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Created timestamp (UTC)")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "wishlist_title": "MacBook Pro M2"
            }
        }
