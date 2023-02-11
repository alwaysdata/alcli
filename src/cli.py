from typing import Optional

from typer import BadParameter, Context, Exit, Option, Typer

from .auth import app as auth_app
from .config import app as config_app
from .config import config, load_localstore
from .requests import auth_requests
from .site import app as site_app
from .types import Format
from .utils import invoke

__version__ = "0.1.0"


def version_callback(value: bool):
    if value:
        print(__version__)
        raise Exit()


app = Typer()


app.add_typer(site_app, name="site")
app.add_typer(auth_app, name="auth")
app.add_typer(config_app, name="config")


@app.callback()
def main(
    ctx: Context,
    api_key: str = Option(
        None,
        help="Your API key from https://admin.alwaysdata.com/token/.",
    ),
    account: str = Option(None, help="The account to perform the actions on."),
    format: Format = Option(
        Format.text, help="The format to return data.", case_sensitive=False
    ),
    version: Optional[bool] = Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
):
    """
    Manage alwaysdata accounts.
    """
    # Break validation when auto-completing
    if ctx.resilient_parsing:
        return

    # Store gobal options
    ctx.ensure_object(dict)
    if api_key:
        ctx.obj["api_key"] = api_key
    if account:
        ctx.obj["account"] = account
    if format:
        ctx.obj["format"] = format

    # Load persisted config
    load_localstore()

    # Initiliaze credentials
    auth_requests(
        api_key=ctx.obj.get("api_key", None),
        account=ctx.obj.get("account", None),
    )


if __name__ == "__main__":
    app()
