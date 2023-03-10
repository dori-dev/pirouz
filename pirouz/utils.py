from hashlib import sha256
from urllib.parse import unquote_plus

from werkzeug import Request


def cleaned_data(request: Request) -> dict:
    request.get_data(as_text=True)
    data = request.data.decode().split('&')
    cleaned_data = {}
    for value in data:
        name, content = value.split('=')
        cleaned_data[name] = unquote_plus(content)
    return cleaned_data


def encrypt(string: str, decode_times=5):
    for _ in range(decode_times):
        string = sha256(string.encode()).hexdigest()
    return string
