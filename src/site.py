from typer import Context, Typer
from requests import get, codes
from tabulate import tabulate

BASE_URL = "https://api.alwaysdata.com/v1/site/"

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
    account = f" account={ctx.obj['account']}" if ctx.obj.get("account") else ''
    credentials = (f"{ctx.obj['api_key']}{account}:", '')
    response = get(BASE_URL, auth=credentials)
    if response.status_code == codes.ok:
        data = [["Name", "ID", "Addresses"]]
        for site in response.json():
            addresses = "\n".join(site["addresses"])
            data.append([site.get('name'), site['id'], addresses])
        print(tabulate(data, headers=("firstrow")))


@app.command()
def info(id: str):
    """
    Display [ID] site's infos
    """
