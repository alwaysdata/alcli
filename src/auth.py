from typing import Optional

from rich.markdown import Markdown
from typer import Context, Exit, Option, Typer, prompt

# from .config import app as config_app
from .config import load as load_config
# from .config import set
from .utils.api import api_url, auth_session, get, post
from .utils.click import forward, invoke
from .utils.console import Renderer, print

# import json


URI = "/token/"


app = Typer()


@app.callback()
def main():
    """
    Manage CLI authentication on the API.
    """


@app.command()
def list(ctx: Context):
    """
    List API tokens.
    """
    config = load_config()

    list = get(api_url(URI))

    # Return Requests response when called outside of Typer
    # (see `login` command)
    if ctx.command.name != "list":
        return list

    if not len(list):
        raise Exit()

    table = [
        {
            "app_name": item.get("app_name"),
            "key": item.get("key"),
            "enabled": not item.get("is_disabled"),
            "allowed_ips": "*" if item.get("allowed_ips") is None else item.get("allowed_ips"),
        }
        for item in list
    ]

    print(table, renderer=Renderer.table, headers=("App Name", "Key", "Enabled", "Allowed IPs"))


@app.command()
def login(
    ctx: Context,
    username: str = Option(None, help="Your alwaysdata's account username."),
    password: str = Option(None, help="Your alwaysdata's account password."),
    api_key: str = Option(None, help="Your API key from https://admin.alwaysdata.com/token/."),
    no_api_key: Optional[bool] = Option(
        None,
        hidden=True,
        help="Prevent using api-key when available (internal use for invoking re-auth).",
    ),
):
    """
    Login user and retrieve an API token.
    """
    config = load_config()

    tokens = list(ctx)
    logged_in = bool(not no_api_key and len(tokens))

    if config.get("output", "format") == Format.json.value:
        content = {"logged_in": logged_in}

    else:
        if logged_in:
            content = "You're logged into the platform!"

        else:
            content = """
Interactive login is currently not available.
        
Please login manually to https://admin.alwaysdata.com/token/, create a token,
and set it with the command `alwaysdata config set api.key <token>`.
    """

    print(content, title="API Login")

    # created = post(api_url, data={"app_name": config["app"]["name"]})
    # if created:
    #     forward(app, login)
    # else:
    #     raise Exit(code=1)

    # else:
    #     invoke(config_app, set, name="api.key", value=cli_token["key"])
