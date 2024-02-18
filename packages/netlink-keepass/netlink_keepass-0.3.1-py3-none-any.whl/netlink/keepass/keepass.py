import pathlib
from pykeepass import PyKeePass
from cryptography.fernet import Fernet


class KeePass(PyKeePass):
    def __init__(self, filename: pathlib.Path, secret: str, keyfile: pathlib.Path = None, token: pathlib.Path = None):
        if token is not None:
            with token.open('rb') as f:
                token_data = f.read()
            password = Fernet(secret.encode()).decrypt(token_data).decode()
        else:
            password = secret
        super().__init__(filename=filename, password=password, keyfile=keyfile)
