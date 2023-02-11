from typing import Optional

from typer import Typer, Context, Option, Exit

from .site import app as site_app


__version__ = "0.1.0"


def version_callback(value: bool):
    if value:
        print(__version__)
        raise Exit()


app = Typer()


app.add_typer(site_app, name="site")


@app.callback()
def main(
    ctx: Context,
    api_key: str = Option(None, prompt=True, hide_input=True, help="Your API key from https://admin.alwaysdata.com/token/."),
    account: str = Option(None, help="The account to perform the actions on."),
    version: Optional[bool] = Option(None, "--version", callback=version_callback, is_eager=True)
):
    ctx.ensure_object(dict)
    if api_key:
        ctx.obj["api_key"] = api_key
    if account:
        ctx.obj["account"] = account


if __name__ == "__main__":
    app()
