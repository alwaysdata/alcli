from typing import Optional

from tabulate import tabulate
from typer import Context, Exit, Option, Typer, prompt

from .config import config
from .config import app as config_app, set
from .requests import auth_requests, get, post
from .types import Format
from .utils import forward, invoke

# import json


URI = "/token/"

app = Typer()


@app.callback()
def auth():
    """
    Manage CLI authentication on the API.
    """


@app.command()
def list(
    ctx: Context,
):
    """
    List API tokens
    """
    api_url = f"{config['api']['base_url']}/{config['api']['version']}/{URI}"

    list = get(api_url, format=ctx.obj["format"])
    if ctx.command.name != "list":
        return list

    if not len(list):
        raise Exit()

    if ctx.obj["format"] == Format.json:
        return print(list)

    headers = ["Application", "Status", "IP", "Key"]
    data = [
        [
            app["app_name"],
            "Disabled" if app["is_disabled"] else "Enabled",
            "-"
            if app["allowed_ips"] is None
            else app["allowed_ips"].replace(" ", "\n"),
            app["key"],
        ]
        for app in list
    ]
    print(tabulate(data, headers=headers))


@app.command()
def login(
    ctx: Context,
    username: str = Option(None, help="Your alwaysdata's account username."),
    password: str = Option(None, help="Your alwaysdata's account password."),
    api_key: str = Option(
        None, help="Your API key from https://admin.alwaysdata.com/token/."
    ),
    no_api_key: Optional[bool] = Option(
        None,
        hidden=True,
        help="Prevent using api-key when available (internal use for invoking re-auth).",
    ),
):
    """
    Login user and retrieve an API token.
    """
    api_url = f"{config['api']['base_url']}/{config['api']['version']}/{URI}"

    # Override global `--api-key` with local
    if api_key:
        ctx.obj["api_key"] = api_key

    if no_api_key:
        ctx.obj.pop("api_key", None)

    # Prompt the user for credentials when no api-key is available
    if no_api_key or ("api_key" not in ctx.obj and not config.has_option("api", "key")):
        if username is None:
            username = prompt("Username")
        if password is None:
            password = prompt("Password", hide_input=True)
        ctx.obj["api_key"] = username

    # Reload credentials from options
    auth_requests(
        api_key=ctx.obj.get("api_key", None),
        account=ctx.obj.get("account", None),
        password=password,
    )

    tokens = list(ctx)
    cli_token = None

    try:
        cli_token = next(t for t in tokens if t["app_name"] == config["app"]["name"])
    except StopIteration:
        pass

    if cli_token is None:
        created = post(api_url, data={"app_name": config["app"]["name"]})
        if created:
            forward(app, login)
        else:
            raise Exit(code=1)

    else:
        invoke(config_app, set, name="api.key", value=cli_token['key'])
        print("You're logged into the platform!")