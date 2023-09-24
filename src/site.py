from typer import Context, Typer

from .config import load as load_config
from .utils.api import api_url, get
from .utils.console import Renderer, print

URI = "site"

app = Typer()


@app.callback()
def site():
    """
    Manage account's sites
    """


@app.command()
def list():
    """
    Display site's list
    """
    config = load_config()
    sites = get(api_url(URI))

    table = [
        {"name": site.get("name", None), "id": site.get("id"), "addresses": site.get("addresses")} for site in sites
    ]

    print(table, renderer=Renderer.table, headers=("Name", "ID", "Addresses"))


@app.command()
def info(id: str):
    """
    Display [ID] site's infos
    """
    site = get(api_url(URI, id))
    infos = {
        key: value
        for key, value in site.items()
        if key in ("type", "command", "working_directory", "environment", "addresses", "name")
    }
    print(
        infos,
        renderer=Renderer.card,
        title=f"Site {site['id']}",
        headers={
            "name": "Name",
            "type": "Type",
            "addresses": "Addresses",
            "working_directory": "Working Directory",
            "environment": "Env",
        },
    )
