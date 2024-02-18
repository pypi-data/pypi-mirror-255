import asyncio
import aiohttp
from .config import API_URL
from .recursively_upload_filepaths import recursively_upload_filepaths

class FuncLive:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        asyncio.run(self._fetch_functions())

    async def _fetch_functions(self):
        async with self.session.get(API_URL + "/functions") as response:
            functions = (await response.json()).get('functions', [])
            for func in functions:
                func_name = func['name']
                setattr(self, func_name, self._sync_wrapper(self._create_function(func_name)))

    def _sync_wrapper(self, coro):
        def run(input_data):
            loop = asyncio.get_event_loop()
            if loop.is_running():
                raise Exception("Can't run synchronous wrapper when event loop is already running")
            else:
                return loop.run_until_complete(coro(input_data))
        return run

    async def _create_function(self, func_name):
        async def func(input_data):
            try:
                modified_input = await recursively_upload_filepaths(input_data, self.session)
                async with self.session.post(API_URL + "/functions/" + func_name,
                                             headers={
                                                 'Authorization': f'Bearer {os.getenv("FUNC_TOKEN")}',
                                                 'Accept': 'application/json',
                                                 'Content-Type': 'application/json'
                                             },
                                             json={'input': modified_input}) as response:
                    return await response.json().get('output')
            except aiohttp.ClientError as e:
                raise Exception(f"There was an error: {str(e)}")
        return func

    async def close(self):
        await self.session.close()


func_live = FuncLive()