from configparser import ConfigParser
from pathlib import Path

from platformdirs import user_config_dir
from typer import Argument, BadParameter, Option, Typer

DEFAULT = {
    "app": {"name": "alcli", "author": "alwaysdata"},
    "api": {
        "base_url": "https://api.alwaysdata.com/",
        "version": "v1",
    },
}

config = ConfigParser()


def _get_config_file_path():
    """
    Return a Path to the config.ini file on the filesystem.
    """
    config_dir_path = user_config_dir(
        config["app"]["name"], config["app"]["author"], roaming=True
    )
    config_path = Path(f"{config_dir_path}/config.ini")
    return config_path


def _save_config_to_file():
    """
    Persist the configuration changes in the filesystem.
    """
    # remove default untouched values
    data = {
        s: {k: v for k, v in config[s].items() if v != DEFAULT.get(s).get(k)}
        for s in config
    }
    # remove empty sections
    data = {n: s for n, s in data.items() if len(data[n])}
    to_save = ConfigParser()
    to_save.read_dict(data)

    config_path = _get_config_file_path()
    config_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    with open(config_path, "w") as config_file:
        to_save.write(config_file)


def load_localstore():
    """
    Populate the config.

    Load config from two sources:
    1. the default values
    2. the local config file
    """
    config.read_dict(DEFAULT)
    config.read(_get_config_file_path())


app = Typer()


@app.callback()
def callback():
    """
    Manage the CLI configuration.

    Use the get and set commands to persists config.

    Examples:

    Read the version of the API use to perform requests:

        $ alwaysdata config get api.version

    Set the account onto which perform requests to `superman`

        $ alwaysdata config set api.account superman
    """


@app.command()
def get(name: str = Argument(..., help="The name of the option to get.")):
    """
    Return the value of the name (<section>.<key>) in the config.
    """
    section, _, name = name.partition(".")
    print(config.get(section, name, fallback=""))


@app.command()
def set(
    name: str = Argument(..., help="The name of the option to set."),
    value: str = Argument(None, help="The value to set the option to."),
    unset: bool = Option(False, "--unset", help="Remove the option in config."),
):
    """
    Save the value for a name (<section>.<key>) in the config.
    """
    section, _, name = name.partition(".")

    if unset:
        config.remove_option(section, name)

    else:
        if value is None:
            raise BadParameter("Missing argument 'VALUE'")
        if not config.has_section(section):
            config.add_section(section)
        config[section][name] = value

    _save_config_to_file()
