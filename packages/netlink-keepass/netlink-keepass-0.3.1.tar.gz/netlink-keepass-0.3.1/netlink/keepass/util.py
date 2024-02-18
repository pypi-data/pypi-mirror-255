import http.client
import json
from collections import namedtuple

from cryptography.fernet import Fernet

FernetToken = namedtuple('FernetToken', ['token', 'key'])


def fernet_token(secret: str):
    key = Fernet.generate_key()
    token = Fernet(key).encrypt(secret.encode())

    return FernetToken(token=token, key=key)


def rest_get(path: str, key: str, port: int = 8666) -> str:
    path = path.strip('/')
    connection = http.client.HTTPConnection('localhost', port=port)
    connection.request('GET', f'/{path}')
    j = json.loads(connection.getresponse().fp.read().decode())
    connection.close()
    result = '\n'.join(j.get(key, '').splitlines())  # need to normalize newline
    return result


def rest_shutdown(port: int = 8666, shutdown: str = '_shutdown') -> str:
    connection = http.client.HTTPConnection('localhost', port=port)
    connection.request('GET', f'/{shutdown}')
    result = connection.getresponse().fp.read().decode()
    connection.close()
    return result
