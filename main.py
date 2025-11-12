import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Media

app = FastAPI(title="Uriel API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MediaCreate(BaseModel):
    title: str
    kind: str
    description: Optional[str] = None
    year: Optional[int] = None
    poster_url: Optional[str] = None
    video_url: Optional[str] = None
    tags: List[str] = []
    rating: Optional[float] = None

@app.get("/")
def read_root():
    return {"message": "Uriel API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

@app.post("/api/media", response_model=dict)
async def create_media(payload: MediaCreate):
    media = Media(**payload.model_dump())
    inserted_id = create_document("media", media)
    return {"id": inserted_id}

@app.get("/api/media", response_model=List[dict])
async def list_media(kind: Optional[str] = None, q: Optional[str] = None):
    filter_dict = {}
    if kind:
        filter_dict["kind"] = kind
    if q:
        filter_dict["title"] = {"$regex": q, "$options": "i"}
    docs = get_documents("media", filter_dict)
    # Convert ObjectId to string
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

@app.post("/api/media/{media_id}/download")
async def increment_download(media_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    try:
        result = db["media"].find_one_and_update(
            {"_id": ObjectId(media_id)},
            {"$inc": {"downloads": 1}, "$set": {"updated_at": __import__("datetime").datetime.utcnow()}},
            return_document=True
        )
        if not result:
            raise HTTPException(status_code=404, detail="Media not found")
        result["id"] = str(result.pop("_id"))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/media/top")
async def top_downloads(limit: int = 10):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    cursor = db["media"].find({}).sort("downloads", -1).limit(limit)
    docs = list(cursor)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
