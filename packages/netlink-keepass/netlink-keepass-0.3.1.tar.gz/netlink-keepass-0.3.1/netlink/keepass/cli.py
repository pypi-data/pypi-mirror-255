import pathlib
import click
from netlink.keepass import reader, fernet_token, rest_get, rest_shutdown


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "-k",
    "--keyfile",
    type=click.Path(
        exists=True,
        dir_okay=False,
        path_type=pathlib.Path,
    ),
    help="'KeePass Key File'",
)
@click.option(
    "-t",
    "--token",
    type=click.Path(
        exists=True,
        dir_okay=False,
        path_type=pathlib.Path,
    ),
    help="Fernet token file",
)
@click.option("-p", "--port", type=int, default=8666, help="Port (default: 8666)")
@click.option(
    "-x",
    "--shutdown",
    default="_shutdown",
    help="Pseudo directory to shutdown server (default: '_shutdown')",
)
@click.argument(
    "filename",
    type=click.Path(
        exists=True,
        dir_okay=False,
        path_type=pathlib.Path,
    ),
)
@click.argument("secret")
def reader_cli(filename, secret, keyfile, token, port, shutdown):
    """
    Start REST server to read KeePass Database FILENAME using SECRET.

    \b
    SECRET is either the 'KeePass Master Password'
           or Fernet key, if Fernet token file is provided.

    Port will be opened for localhost only.
    """
    reader(filename=filename, secret=secret, keyfile=keyfile, token=token, port=port, shutdown=shutdown)


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "-t",
    "--token",
    type=click.Path(
        dir_okay=False,
        path_type=pathlib.Path,
    ),
    default=pathlib.Path('token'),
    help="Fernet token file",
)
@click.argument("secret")
def fernet_token_cli(secret, token):
    """
    Create Fernet Token for SECRET.
    """
    result = fernet_token(secret=secret)
    with token.open("wb") as token_file:
        token_file.write(result.token)

    print(result.key.decode("utf-8"))


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-p", "--port", type=int, default=8666, help="Port (default: 8666)")
@click.argument("path")
@click.argument("key")
def rest_get_cli(path, key, port):
    """
    Retrieve PATH from local REST server and print content of key.
    """
    print(rest_get(path, key, port))


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-p", "--port", type=int, default=8666, help="Port (default: 8666)")
@click.option(
    "-x",
    "--shutdown",
    default="_shutdown",
    help="Pseudo directory to shutdown server (default: '_shutdown')",
)
def rest_shutdown_cli(port, shutdown):
    """
    Shutdown REST server
    """
    rest_shutdown(port, shutdown)
