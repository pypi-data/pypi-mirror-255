import os
import httpx
from .config import API_URL
from .recursively_upload_filepaths import recursively_upload_filepaths

class FuncLive:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def initialize(self):
        await self._fetch_functions()

    async def _fetch_functions(self):
        response = await self.client.get(f"{API_URL}/functions")
        functions = response.json().get('functions', [])

        for func in functions:
            func_name = func['name']
            setattr(self, func_name, self._create_function(func_name))

    def _create_function(self, func_name):
        async def func(input_data):
            try:
                modified_input = await recursively_upload_filepaths(input_data)
                response = await self.client.post(f"{API_URL}/functions/{func_name}",
                                                  headers={
                                                      'Authorization': f'Bearer {os.getenv("FUNC_TOKEN")}',
                                                      'Accept': 'application/json',
                                                      'Content-Type': 'application/json'
                                                  },
                                                  json={'input': modified_input})
                return response.json().get('output')
            except httpx.RequestError as e:
                raise Exception(f"There was an error: {str(e)}")

        return func

async def init_func():
    func_live = FuncLive()
    await func_live.initialize()
    return func_live