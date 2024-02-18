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
        functions.append({'name': 'token'})

        for func in functions:
            func_name = func['name']
            setattr(self, func_name, self._create_function(func_name))

    def _create_function(self, func_name):
        def func(input_data=None):
            if func_name == 'token' and isinstance(input_data, str):
                os.environ['FUNC_TOKEN'] = input_data
                trimmed_token = input_data[:10] + '...' + input_data[-10:]
                return f"Token updated successfully to {trimmed_token}, Your token is trimmed for security purposes. To see the full token, use os.getenv('FUNC_TOKEN'). If you want to update the token, use func_live.token('your_token')."

            try:
                modified_input = None if input_data is None else recursively_upload_filepaths(input_data)           
                payload = {'input': modified_input} if modified_input is not None else {}
                
                token = os.getenv("FUNC_TOKEN")
                response = requests.post(f"{API_URL}/functions/{func_name}",
                                         headers={
                                             'Authorization': f'Bearer {token}',
                                             'Accept': 'application/json',
                                             'Content-Type': 'application/json'
                                         },
                                         json=payload)
                return response.json().get('output')
            except requests.RequestException as e:
                raise Exception(f"There was an error: {str(e)}")

        return func

func = FuncLive()
