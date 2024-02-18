import requests
from pathlib import Path
from func_live.config import API_URL

def upload_file(input_path):
    filename = Path(input_path).name
    with open(input_path, 'rb') as file:
        response = requests.post(f"{API_URL}/upload-file",
                                 files={'file': (filename, file)})
    response_data = response.json()
    return response_data['url']