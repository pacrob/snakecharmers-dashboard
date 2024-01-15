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
import httpx
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
GITHUB_API_TOKEN = os.environ.get("GITHUB_API_TOKEN")
GITHUB_CLASSIC_API_TOKEN = os.environ.get("GITHUB_CLASSIC_API_TOKEN")


# Database setup
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class DataModel(Base):
    """Data model for storing data from external API."""

    __tablename__ = "data"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    data = Column(String)


Base.metadata.create_all(bind=engine)


libs_to_check = [
    "web3.py",
    "eth-account",
    "eth-abi",
    # "eth-utils",
    # "eth-keys",
    # "eth-typing",
    # "eth-hash",
]


async def fetch_newsfragment_data():
    """Fetch data from external API and return it as a JSON object."""
    async with httpx.AsyncClient() as client:
        # Replace with your actual API endpoint

        newsfragment_data = []

        # async for lib in libs_to_check:
        for lib in libs_to_check:
            url = f"https://api.github.com/repos/ethereum/{lib}/contents/newsfragments"
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {GITHUB_CLASSIC_API_TOKEN}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            response = await client.get(url, headers=headers)
            newsfragment_data.append(response.json())

        return newsfragment_data


# Background task to fetch data every minute
async def background_fetch_newsfragments():
    """Fetch data from external API every minute and store it in the database."""
    while True:
        data = await fetch_newsfragment_data()
        print(data)
        # db = SessionLocal()
        # db_data = DataModel(data=str(data))
        # db.add(db_data)
        # db.commit()
        # db.close()
        await asyncio.sleep(30)


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
    latest_data = await fetch_newsfragment_data()
    if latest_data:
        return {"data": latest_data}
    raise HTTPException(status_code=404, detail="Data not found")


# async def fetch_data():
#     """Fetch data from external API and return it as a JSON object."""
#     async with httpx.AsyncClient() as client:
#         # Replace with your actual API endpoint
#         response = await client.get("https://api.external.com/data")
#         return response.json()

# # Background task to fetch data every minute
# async def background_fetch():
#     """Fetch data from external API every minute and store it in the database."""
#     while True:
#         data = await fetch_data()
#         db = SessionLocal()
#         db_data = DataModel(data=str(data))
#         db.add(db_data)
#         db.commit()
#         db.close()
#         await asyncio.sleep(60)


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


# Run with: uvicorn backend_app:app --reload
