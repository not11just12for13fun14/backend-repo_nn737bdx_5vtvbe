from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
    brand: Optional[str] = Field(None, description="Brand name")
    sport: Optional[str] = Field(None, description="Related sport")
    image: Optional[str] = Field(None, description="Primary image URL")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating 0-5")
