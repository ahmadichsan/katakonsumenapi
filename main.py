from fastapi import FastAPI
import uvicorn
import os
from dotenv import load_dotenv
from app.routes import reviews, wishlist

# Load environment variables
load_dotenv(dotenv_path=".env")

app = FastAPI(title="KataKonsumenAPI", version="1.0.0")

# Include Routers
app.include_router(reviews.router)
app.include_router(wishlist.router)

@app.get("/")
def home():
    return {"message": "Welcome to KataKonsumen API"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Default ke 8000 jika tidak ada PORT di .env
    print(f"Running on port: {port}")   # Cek apakah port terbaca
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

# Jalankan server: uvicorn main:app --reload
