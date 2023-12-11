from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import httpx
import asyncio
import datetime

# Database setup
DATABASE_URL = "sqlite:///./test.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DataModel(Base):
    __tablename__ = "data"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    data = Column(String)

Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# Async function to fetch data from external API
async def fetch_data():
    async with httpx.AsyncClient() as client:
        # Replace with your actual API endpoint
        response = await client.get("https://api.external.com/data")
        return response.json()

# Background task to fetch data every minute
async def background_fetch():
    while True:
        data = await fetch_data()
        db = SessionLocal()
        db_data = DataModel(data=str(data))
        db.add(db_data)
        db.commit()
        db.close()
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_fetch())

# Endpoint to get the latest data
@app.get("/data")
async def get_data():
    db = SessionLocal()
    latest_data = db.query(DataModel).order_by(DataModel.id.desc()).first()
    db.close()
    if latest_data:
        return {"data": latest_data.data}
    raise HTTPException(status_code=404, detail="Data not found")

# Run with: uvicorn backend_app:app --reload
