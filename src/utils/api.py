from json import dumps

from requests import codes
from requests import get as r_get
from requests import head as r_head
from requests import post as r_post
from rich.status import Status
from typer import Exit

from ..config import load as load_config
from .console import Format, console, print

_auth = None


class TokenNotFound(ValueError):
    """Failed to get Token for scrapping"""


def api_url(URI, path=None):
    config = load_config()
    return f"{config.get('api', 'base_url')}/{config.get('api', 'version')}/{URI}/{path if path is not None else ''}"


def auth_session(api_key, account=None, password=""):
    """
    Generate the credentials to be used on API
    """
    global _auth

    token = api_key

    if account:
        token = f"{token} account={account}"

    _auth = (token, password)


_spinner = Status("Loading...", console=console, spinner="dots")


def _ensure_login(func):
    def wrapper(*args, **kwargs):
        check_auth = r_head(api_url("/token/"), auth=_auth)
        if check_auth.status_code == codes.unauthorized:
            from ..auth import app as auth_app
            from ..auth import login
            from .click import invoke

            if invoke(auth_app, login, no_api_key=True):
                return func(*args, **kwargs)
            else:
                raise Exit(code=1)

        else:
            return func(*args, **kwargs)

    return wrapper


@_ensure_login
def get(url):
    # TODO: do not show spinner under --no-pretty mode
    _spinner.start()

    response = r_get(url, auth=_auth)

    if response.status_code != codes.ok:
        raise Exit(code=1)

    _spinner.stop()
    return response.json()


@_ensure_login
def post(url, data):
    response = r_post(url, auth=_auth, data=dumps(data))

    return response.status_code == codes.created
