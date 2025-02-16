# 🗂 KataKonsumen – Product & Service Review System

**KataKonsumen** is a platform for collecting and displaying user reviews of products or services. It is integrated with **Pusaka CMS** and **Pusaka Chat**, enabling users to submit reviews directly through an AI-powered chat agent.

---

## 🚀 **Main Features:**
- 📒 **Create Review:**  
  - Flat payload (compatible with Pusaka CMS).  
  - Validates and uploads only valid image URLs (`image/*`).  
  - Stores images in **Supabase Storage** under `/username/unique-filename` format.  
  - Full sync: If any upload fails, the entire request is rejected.  
- 🔍 **Search Review:**  
  - Filters are provided via the request body (not query parameters).  
  - Supports substring `LIKE` search (case-insensitive) for all string fields.  
- 📑 **Get Review Detail:**  
  - Accepts `review_id` from the request body.  
- ❤️ **Wishlist Management:**  
  - `username` is mandatory (primary identifier).  
  - Supports substring `LIKE` search for `wishlist_title`.  

---

## 🛠️ **Technology Stack:**
- **Backend:** FastAPI (Python)
- **Database:** MongoDB Atlas (NoSQL)
- **Storage:** Supabase Storage
- **Integration:** Pusaka CMS & Pusaka Chat

---

## ⚙️ **Environment Configuration (`.env`):**
Before running the project, create a `.env` file with the following content:

```ini
# MongoDB
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=reviewdb

# Supabase
SUPABASE_URL=https://your-project-url.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_BUCKET=kata-konsumen-review-images

# Server
PORT=8080
```

---

## 💻 **How to Run the Project:**

- Clone the Repository
- Activate Virtual Environment:

```ini
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

- Install Dependencies:
```ini
pip install -r requirements.txt
```

- Run the Server
```ini
python main.py
```

---

## ❤️ **Contributors:**
- Project Owner & Developer: Ahmad Ichsan Baihaqi
- AI Assistant: ChatGPT (OpenAI). Love you, ChatGPT.
