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


LIBS_TO_CHECK = [
    "web3.py",
    "eth-account",
    "eth-abi",
    # "eth-utils",
    # "eth-keys",
    # "eth-typing",
    # "eth-hash",
]

NEWSFRAGMENT_FILES_TO_IGNORE = [
    "README.md",
    "README.rst",
    "README",
    "validate_files.py",
]

GITHUB_API_HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_CLASSIC_API_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


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


async def fetch_contents_of_newsfragments_folder(lib: str, client: httpx.AsyncClient):
    """Fetch contents of the newsfragments folder of a given lib."""
    url = f"https://api.github.com/repos/ethereum/{lib}/contents/newsfragments"
    response = await client.get(url, headers=GITHUB_API_HEADERS)
    return response.json()


async def fetch_created_for_a_newsfragment_file(
    lib: str, filename: str, client: httpx.AsyncClient
):
    """Fetch the date of creation for a single newsfragment file."""
    url = (
        f"https://api.github.com/repos/ethereum/{lib}/commits?path=newsfragments"
        f"/{filename}"
    )
    response = await client.get(url, headers=GITHUB_API_HEADERS)
    return response.json()


async def fetch_newsfragment_data_for_single_lib(lib: str) -> list[str]:
    """Fetch newsfragment data for a single library from the github api."""
    async with httpx.AsyncClient() as client:
        response = await fetch_contents_of_newsfragments_folder(lib, client)

        # parse response down to just the newsfragment filenames
        newsfragment_filenames = [
            file["name"]
            for file in response
            if file["name"] not in NEWSFRAGMENT_FILES_TO_IGNORE
        ]

        return newsfragment_filenames


async def fetch_all_newsfragment_data():
    """Fetch data from external API and return it as a JSON object."""
    lib_info = {}
    for lib in LIBS_TO_CHECK:
        newsfragment_filenames = await fetch_newsfragment_data_for_single_lib(lib)
        lib_info[lib] = newsfragment_filenames

    return lib_info


# Background task to fetch data every minute
async def background_fetch_newsfragments():
    """Fetch data from external API every minute and store it in the database."""
    while True:
        data = await fetch_all_newsfragment_data()
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
    latest_data = await fetch_all_newsfragment_data()
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
