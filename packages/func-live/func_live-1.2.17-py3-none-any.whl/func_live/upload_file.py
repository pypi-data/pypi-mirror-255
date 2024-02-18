from aiohttp import FormData
from pathlib import Path
from .config import API_URL

async def upload_file(input_path, session):
    # Read the file's content
    filename = Path(input_path).name
    data = FormData()
    data.add_field('file', open(input_path, 'rb'), filename=filename)

    async with session.post(f"{API_URL}/upload-file", data=data) as response:
        response_data = await response.json()
        return response_data['url']
