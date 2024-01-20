import asyncio
from contextlib import (
    asynccontextmanager,
)
import datetime
import os

from fastapi import (
    FastAPI,
    HTTPException,
)
from newsfragments import (
    background_fetch_newsfragments,
    fetch_all_newsfragment_data_from_github_api,
)
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
)

DATABASE_URL = os.environ.get("DATABASE_URL")

# Database setup
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class DataModel(Base):
    """Data model for storing data from external API."""

    __tablename__ = "basic_data"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    data = Column(String)


Base.metadata.create_all(bind=engine)


@asynccontextmanager  # type: ignore
async def lifespan(app: FastAPI):
    """Context manager to run background tasks during the lifespan of the app."""
    asyncio.create_task(background_fetch_newsfragments())


# FastAPI app
# app = FastAPI(lifespan=lifespan)
app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello World"}


@app.get("/newsfragments")
async def get_newsfragments():
    """Get the latest data from the database."""
    # db = SessionLocal()
    # latest_data = db.query(DataModel).order_by(DataModel.id.desc()).first()
    # db.close()
    latest_data = await fetch_all_newsfragment_data_from_github_api()
    if latest_data:
        return {"data": latest_data}
    raise HTTPException(status_code=404, detail="Data not found")


# # TODO on_event is deprecated, find a better way to start the background task
# @app.on_event("startup")
# async def startup_event():
#     """Start the background task when the app starts.""" ""
#     asyncio.create_task(background_fetch())


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


@app.post("/data")
async def post_data(data: str):
    """Post data to the database."""
    print(f"{data=}")
    db = SessionLocal()
    db_data = DataModel(data=data)
    db.add(db_data)
    db.commit()
    db.close()
    return {"data": data}


# Run with: uvicorn backend_app:app --reload
