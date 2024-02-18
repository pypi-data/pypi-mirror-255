from .upload_file import upload_file
from aiohttp import ClientSession
from pathlib import Path
import asyncio

async def is_object(thing):
    return not isinstance(thing, list) and isinstance(thing, dict)

async def recursively_upload_filepaths(input, session=None):
    async with ClientSession() as session:
        if isinstance(input, str):
            if Path(input).exists():
                return await upload_file(input, session)
            return input
        if await is_object(input):
            output = {}
            tasks = [asyncio.create_task(recursively_upload_filepaths(value, session)) for value in input.values()]
            results = await asyncio.gather(*tasks)
            for key, value in zip(input.keys(), results):
                output[key] = value
            return output
        if isinstance(input, list):
            return [await recursively_upload_filepaths(item, session) for item in input]
        return input