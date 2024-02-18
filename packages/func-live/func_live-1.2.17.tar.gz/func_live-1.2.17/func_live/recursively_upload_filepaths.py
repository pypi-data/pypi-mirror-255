from .upload_file import upload_file
from aiohttp import ClientSession
from pathlib import Path
import asyncio

async def is_object(thing):
    return isinstance(thing, dict)

async def recursively_upload_filepaths(input, session=None):
    if session is None:
        async with ClientSession() as new_session:
            return await recursively_handle_input(input, new_session)
    else:
        return await recursively_handle_input(input, session)

async def recursively_handle_input(input, session):
    if isinstance(input, str) and Path(input).is_file():
        return await upload_file(input, session)
    elif isinstance(input, dict):
        tasks = {k: asyncio.create_task(recursively_upload_filepaths(v, session)) for k, v in input.items()}
        return {k: await v for k, v in tasks.items()}
    elif isinstance(input, list):
        return [await recursively_upload_filepaths(item, session) for item in input]
    return input
