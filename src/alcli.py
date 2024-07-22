from pathlib import Path
from typing import Optional

from typer import BadParameter, Context, Exit, FileText, Option, Typer

from .auth import app as auth_app
from .config import app as config_app
from .config import load as load_config
from .site import app as site_app
from .utils.api import auth_session
from .utils.console import Format, print

__version__ = "0.1.0"


def version_callback(is_called: bool):
    if is_called:
        print(__version__, no_pretty=True)
        raise Exit()


app = Typer()

app.add_typer(site_app, name="site")
app.add_typer(auth_app, name="auth")
app.add_typer(config_app, name="config")


@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    api_key: str = Option(
        None,
        help="Your API key from https://admin.alwaysdata.com/token/.",
    ),
    api_account: str = Option(None, "--account", "-a", help="The account to perform the actions on."),
    config_file: Path = Option(
        None,
        "--config",
        exists=True,
        dir_okay=False,
        help="An alternative path to the config file.",
    ),
    output_format: Format = Option(
        Format.text,
        "--format",
        "-f",
        help="The format to return data.",
        case_sensitive=False,
    ),
    output_pretty: bool = Option(True, "--pretty/--no-pretty", help="Enable/Disable fancy user output."),
    version: Optional[bool] = Option(None, "--version", callback=version_callback, is_eager=True),
):
    """
    Manage alwaysdata accounts' settings and workflows.
    """
    # Break validation when auto-completing
    if ctx.resilient_parsing:
        return

    # Load config and options
    ctx.obj = load_config(
        config_file=config_file,
        session_dict={
            option: f"{input}"
            for option, input in locals().items()
            if option not in ("ctx", "version") and input is not None
        },
    )

    # Initialize credentials
    auth_session(
        api_key=ctx.obj.get("api", "key"),
        account=ctx.obj.get("api", "account"),
    )


if __name__ == "__main__":
    app()
