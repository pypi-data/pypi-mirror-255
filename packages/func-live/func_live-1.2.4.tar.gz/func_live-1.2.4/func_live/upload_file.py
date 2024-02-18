from pathlib import Path
from .config import API_URL

async def upload_file(input_path, session):
    filename = Path(input_path).name
    with open(input_path, 'rb') as file:
        files = {'file': (filename, file)}
        async with session.post(f"{API_URL}/upload-file", data=files) as response:
            return (await response.json())['url']
