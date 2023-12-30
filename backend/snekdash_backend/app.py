import asyncio
import datetime

from fastapi import (
    FastAPI,
    HTTPException,
)
import httpx
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import (
    declarative_base,
)
from sqlalchemy.orm import (
    sessionmaker,
)

# Database setup
DATABASE_URL = "sqlite:///./test.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DataModel(Base):  # type: ignore
    """Data model for storing data from external API."""

    __tablename__ = "data"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    data = Column(String)


Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()


async def fetch_data():
    """Fetch data from external API and return it as a JSON object."""
    async with httpx.AsyncClient() as client:
        # Replace with your actual API endpoint
        response = await client.get("https://api.external.com/data")
        return response.json()


# Background task to fetch data every minute
async def background_fetch():
    """Fetch data from external API every minute and store it in the database."""
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
    """Start the background task when the app starts.""" ""
    asyncio.create_task(background_fetch())


# Endpoint to get the latest data
@app.get("/data")
async def get_data():
    """Get the latest data from the database."""
    db = SessionLocal()
    latest_data = db.query(DataModel).order_by(DataModel.id.desc()).first()
    db.close()
    if latest_data:
        return {"data": latest_data.data}
    raise HTTPException(status_code=404, detail="Data not found")


# Run with: uvicorn backend_app:app --reload
