from tabulate import tabulate
from typer import Context, Typer

from .config import config
from .requests import get

URI = "/site/"

app = Typer()


@app.callback()
def site(ctx: Context):
    """
    Manage account's sites
    """


@app.command()
def list(ctx: Context):
    """
    Display site's list
    """
    api_url = f"{config['api']['base_url']}/{config['api']['version']}/{URI}"

    sites = get(api_url)
    headers = ["Name", "ID", "Addresses"]
    data = [
        (site.get("name", None), site["id"], "\n".join(site["addresses"]))
        for site in sites
    ]
    print(tabulate(data, headers=headers))


@app.command()
def info(id: str):
    """
    Display [ID] site's infos
    """
