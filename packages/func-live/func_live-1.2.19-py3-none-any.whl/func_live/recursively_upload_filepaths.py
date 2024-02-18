from .upload_file import upload_file 
from pathlib import Path
import requests

def is_object(thing):
    return isinstance(thing, dict)

def recursively_upload_filepaths(input, session=None):
    if session is None:
        with requests.Session() as new_session:
            return recursively_handle_input(input, new_session)
    else:
        return recursively_handle_input(input, session)

def recursively_handle_input(input, session):
    if isinstance(input, str) and Path(input).is_file():
        return upload_file(input, session)
    elif isinstance(input, dict):
        return {k: recursively_upload_filepaths(v, session) for k, v in input.items()}
    elif isinstance(input, list):
        return [recursively_upload_filepaths(item, session) for item in input]
    return input
