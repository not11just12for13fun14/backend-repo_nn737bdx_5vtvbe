import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product as ProductSchema

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Sports E-commerce API is running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


class ProductOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
    brand: Optional[str] = None
    sport: Optional[str] = None
    image: Optional[str] = None
    rating: Optional[float] = None


@app.get("/api/products", response_model=List[ProductOut])
def list_products(category: Optional[str] = None, sport: Optional[str] = None, q: Optional[str] = None):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    filter_dict = {}
    if category:
        filter_dict["category"] = category
    if sport:
        filter_dict["sport"] = sport
    if q:
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"brand": {"$regex": q, "$options": "i"}},
        ]

    docs = get_documents("product", filter_dict)
    products: List[ProductOut] = []
    for d in docs:
        products.append(
            ProductOut(
                id=str(d.get("_id", "")),
                title=d.get("title"),
                description=d.get("description"),
                price=float(d.get("price", 0)),
                category=d.get("category", "Other"),
                in_stock=bool(d.get("in_stock", True)),
                brand=d.get("brand"),
                sport=d.get("sport"),
                image=d.get("image"),
                rating=float(d.get("rating", 0)) if d.get("rating") is not None else None,
            )
        )
    return products


@app.post("/api/products/seed")
def seed_products():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    count = db["product"].count_documents({})
    if count > 0:
        return {"inserted": 0, "message": "Products already seeded"}

    sample_products = [
        {
            "title": "Pro Sprint Running Shoes",
            "description": "Lightweight running shoes with responsive cushioning for race day.",
            "price": 129.99,
            "category": "Footwear",
            "brand": "Aerofleet",
            "sport": "Running",
            "in_stock": True,
            "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=1400&auto=format&fit=crop",
            "rating": 4.7,
        },
        {
            "title": "Elite Match Soccer Ball",
            "description": "FIFA Quality Pro ball with textured surface for superior control.",
            "price": 59.99,
            "category": "Equipment",
            "brand": "VectorSport",
            "sport": "Football",
            "in_stock": True,
            "image": "https://images.unsplash.com/photo-1593341646944-b3b4b3bb2d8b?q=80&w=1400&auto=format&fit=crop",
            "rating": 4.5,
        },
        {
            "title": "Carbon Pro Tennis Racket",
            "description": "Premium graphite frame for power and precision on every swing.",
            "price": 199.0,
            "category": "Equipment",
            "brand": "StrikeLabs",
            "sport": "Tennis",
            "in_stock": True,
            "image": "https://images.unsplash.com/photo-1521417531039-56b2b33f89d8?q=80&w=1400&auto=format&fit=crop",
            "rating": 4.6,
        },
        {
            "title": "Performance Training Tee",
            "description": "Moisture-wicking fabric with mesh ventilation for high-intensity workouts.",
            "price": 29.99,
            "category": "Apparel",
            "brand": "PulseGear",
            "sport": "Gym",
            "in_stock": True,
            "image": "https://images.unsplash.com/photo-1594386304855-24b9f191e4dd?q=80&w=1400&auto=format&fit=crop",
            "rating": 4.3,
        },
        {
            "title": "All-Court Basketball",
            "description": "Durable composite leather cover for indoor and outdoor play.",
            "price": 39.99,
            "category": "Equipment",
            "brand": "HoopX",
            "sport": "Basketball",
            "in_stock": True,
            "image": "https://images.unsplash.com/photo-1519861531473-9200262188bf?q=80&w=1400&auto=format&fit=crop",
            "rating": 4.4,
        },
        {
            "title": "Pro Cycling Helmet",
            "description": "Aerodynamic shell with MIPS for enhanced safety and airflow.",
            "price": 89.99,
            "category": "Protective Gear",
            "brand": "VeloCore",
            "sport": "Cycling",
            "in_stock": True,
            "image": "https://images.unsplash.com/photo-1517649763962-0c623066013b?q=80&w=1400&auto=format&fit=crop",
            "rating": 4.8,
        },
    ]

    inserted = 0
    for p in sample_products:
        create_document("product", p)
        inserted += 1

    return {"inserted": inserted}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
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

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
