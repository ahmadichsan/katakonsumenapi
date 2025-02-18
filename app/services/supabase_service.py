import requests
import uuid
import os
from supabase import create_client, Client
from typing import Any

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def is_image_url(image_url: str) -> bool:
    """Check if URL is an image based on Content-Type."""
    try:
        response = requests.head(image_url, timeout=5)
        content_type = response.headers.get("Content-Type", "")
        return content_type.startswith("image/")
    except Exception:
        return False

def download_image(image_url: str) -> bytes:
    """Download image from URL if valid, else return None."""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"Skipped non-image content from {image_url} (Content-Type: {content_type})")
            return None
        return response.content
    except Exception as e:
        print(f"Failed to download image from {image_url}: {e}")
        return None

def upload_to_supabase(username: str, image_bytes: bytes) -> str:
    """Upload image to Supabase Storage with path /<username>/<unique-file-name>."""
    try:
        blob_name = f"{username}/{uuid.uuid4()}.jpg"
        response: Any = supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=blob_name,
            file=image_bytes,
            file_options={"content-type": "image/jpeg", "cache-control": "3600"},
        )

        # Validasi hasil upload
        if hasattr(response, 'status_code') and response.status_code not in [200, 201]:
            raise Exception(f"Upload failed with status code {response.status_code}")

        return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{blob_name}"

    except Exception as e:
        print(f"Failed to upload image to Supabase: {e}")
        return None

def delete_from_supabase(image_url: str):
    """
    Delete image from Supabase Storage using image URL.
    """
    try:
        path = image_url.split(f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/")[-1]
        response = supabase.storage.from_(SUPABASE_BUCKET).remove([path])

        if response and response[0].get("error"):
            print(f"Failed to delete image from Supabase: {response[0]['error']}")
        else:
            print(f"Deleted image from Supabase: {image_url}")
    except Exception as e:
        print(f"Error deleting image from Supabase: {e}")
