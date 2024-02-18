import os
import signal
import pathlib

import fastapi
import uvicorn
from pykeepass.entry import reserved_keys

from netlink.keepass.keepass import KeePass

reserved_keys = set([i.lower() for i in reserved_keys if i not in ('History', 'IconID', 'Times')])


app = fastapi.FastAPI()


# noinspection PyUnresolvedReferences
@app.get("/{full_path:path}")
async def get_value(full_path: str):
    if full_path.startswith(app.state.shutdown):
        os.kill(os.getpid(), signal.SIGTERM)
        return fastapi.Response(status_code=200, content='Server shutting down...')
    kp_path = full_path.split('/')
    entry = app.state.kp.find_entries(path=full_path.split('/'))
    if entry is None:
        raise fastapi.HTTPException(status_code=404, detail=f"{full_path} not found")
    result = {k: getattr(entry, k) for k in reserved_keys}
    result.update(entry.custom_properties)
    return result


# noinspection PyUnresolvedReferences
def reader(filename: pathlib.Path, secret: str, keyfile: pathlib.Path = None, token: pathlib.Path = None, port: int = 8666, shutdown: str = '_shutdown') -> None:
    """Start REST server to read KeePass

    :param filename: KeePass Database file
    :param secret: Password for KeePass database or Key for Fernet
    :param keyfile: KeePass key file
    :param token: Fernet token file
    :param port: Server port
    :param shutdown: URL path to shutdown server
    """
    app.state.kp = KeePass(filename=filename,
                           secret=secret,
                           keyfile=keyfile,
                           token=token)
    app.state.shutdown = shutdown
    uvicorn.run(app, port=port, log_level="info")
