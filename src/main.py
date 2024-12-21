from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import datetime

app = FastAPI(title="Demo API")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(Text)

# Pydantic Models
class ItemCreate(BaseModel):
    name: str
    description: str

class Item(ItemCreate):
    id: int
    
    class Config:
        orm_mode = True

# Database Dependency
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Welcome to the Demo API"}

@app.get("/items", response_model=List[Item])
async def get_items():
    with get_db() as db:
        items = db.query(ItemDB).all()
        return items

@app.post("/items", response_model=Item)
async def create_item(item: ItemCreate):
    with get_db() as db:
        db_item = ItemDB(**item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    with get_db() as db:
        item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        with get_db() as db:
            db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
