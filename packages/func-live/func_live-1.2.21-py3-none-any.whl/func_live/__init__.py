import os
import requests
from .config import API_URL
from .recursively_upload_filepaths import recursively_upload_filepaths

class FuncLive:
    def __init__(self):
        self._fetch_functions()

    def _fetch_functions(self):
        response = requests.get(f"{API_URL}/functions")
        functions = response.json().get('functions', [])

        for func in functions:
            func_name = func['name']
            setattr(self, func_name, self._create_function(func_name))

    def _create_function(self, func_name):
        def func(input_data):
            try:
                modified_input = recursively_upload_filepaths(input_data)
                response = requests.post(f"{API_URL}/functions/{func_name}",
                                         headers={
                                             'Authorization': f'Bearer {os.getenv("FUNC_TOKEN")}',
                                             'Accept': 'application/json',
                                             'Content-Type': 'application/json'
                                         },
                                         json={'input': modified_input})
                return response.json().get('output')
            except requests.RequestException as e:
                raise Exception(f"There was an error: {str(e)}")

        return func

func_live = FuncLive()