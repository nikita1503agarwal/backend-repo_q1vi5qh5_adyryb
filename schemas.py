"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Uriel app schemas

class Media(BaseModel):
    """
    Media items for movies, series, anime
    Collection name: "media"
    """
    title: str = Field(..., min_length=1)
    kind: Literal["movie", "series", "anime"] = Field(..., description="Type of media")
    description: Optional[str] = Field(None, max_length=2000)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    poster_url: Optional[HttpUrl] = Field(None, description="Poster image URL")
    video_url: Optional[HttpUrl] = Field(None, description="Streaming/Download URL")
    tags: List[str] = Field(default_factory=list)
    rating: Optional[float] = Field(None, ge=0, le=10)
    downloads: int = Field(0, ge=0, description="Download count")
