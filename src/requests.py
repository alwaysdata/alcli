from json import dumps

from typer import Exit

from requests import codes
from requests import get as r_get
from requests import post as r_post

from .config import config
from .types import Format

_auth = None


def auth_requests(api_key=None, account=None, password=""):
    """
    Generate the credentials to be used on API
    """
    global _auth

    token = config.get("api", "key", fallback="")
    if api_key:
        token = api_key

    if account:
        token = f"{token} account={account}"
    elif config.has_option("api", "account"):
        token = f"{token} account={config['api']['account']}"

    _auth = (token, password)


def get(url, format=Format.text):
    response = r_get(url, auth=_auth)

    if response.status_code == codes.unauthorized:
        from .auth import app as auth_app
        from .auth import login
        from .utils import invoke

        invoke(auth_app, login, no_api_key=True)
        return get(url, format=format)

    if response.status_code != codes.ok:
        raise Exit(code=1)

    return response.json()


def post(url, data):
    response = r_post(url, auth=_auth, data=dumps(data))

    if response.status_code == codes.unauthorized:
        from .auth import app as auth_app
        from .auth import login
        from .utils import invoke

        invoke(auth_app, login, no_api_key=True)
        return post(url, data)

    return response.status_code == codes.created
