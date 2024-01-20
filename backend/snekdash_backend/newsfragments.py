import asyncio
import asyncio
import os

import httpx

GITHUB_API_TOKEN = os.environ.get("GITHUB_API_TOKEN")
GITHUB_CLASSIC_API_TOKEN = os.environ.get("GITHUB_CLASSIC_API_TOKEN")
GITHUB_API_HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_CLASSIC_API_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}
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

async def fetch_contents_of_newsfragments_folder(lib: str, client: httpx.AsyncClient):
    """Fetch contents of the newsfragments folder of a given lib."""
    url = f"https://api.github.com/repos/ethereum/{lib}/contents/newsfragments"
    response = await client.get(url, headers=GITHUB_API_HEADERS)
    return response.json()


async def fetch_commit_date_for_a_newsfragment_file(
    lib: str, filename: str, client: httpx.AsyncClient
):
    """Fetch the date of creation for a single newsfragment file."""
    url = (
        f"https://api.github.com/repos/ethereum/{lib}/commits?path=newsfragments"
        f"/{filename}"
    )
    response = await client.get(url, headers=GITHUB_API_HEADERS)
    return response.json()


async def fetch_newsfragment_data_for_single_lib(lib: str) -> dict[str, str]:
    """Fetch newsfragment data for a single library from the github api."""
    async with httpx.AsyncClient() as client:
        response_list = await fetch_contents_of_newsfragments_folder(lib, client)

        # parse response down to just the newsfragment filenames
        newsfragment_filenames = [
            file["name"]
            for file in response_list
            if file["name"] not in NEWSFRAGMENT_FILES_TO_IGNORE
        ]

        # fetch the commit date for each newsfragment file
        file_commit_dates = {}
        for filename in newsfragment_filenames:
            response = await fetch_commit_date_for_a_newsfragment_file(
                lib, filename, client
            )
            # ...["committer"]["date"] parses the date of the most recent commit to
            # the file. If the date of first authorship is desired, use
            # ...["author"]["date"] instead.
            file_commit_dates[filename] = response[0]["commit"]["committer"]["date"]

        return file_commit_dates


async def fetch_all_newsfragment_data_from_github_api():
    """Fetch data from external API and return it as a JSON object."""
    lib_info = {}
    for lib in LIBS_TO_CHECK:
        newsfragment_commit_dates = await fetch_newsfragment_data_for_single_lib(lib)
        lib_info[lib] = newsfragment_commit_dates

    return lib_info


# Background task to fetch data every minute
async def background_fetch_newsfragments():
    """Fetch data from external API every minute and store it in the database."""
    while True:
        data = await fetch_all_newsfragment_data_from_github_api()
        print(data)
        # db = SessionLocal()
        # db_data = DataModel(data=str(data))
        # db.add(db_data)
        # db.commit()
        # db.close()
        await asyncio.sleep(30)