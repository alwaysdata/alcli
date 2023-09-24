import collections
from configparser import ConfigParser
from pathlib import Path
from typing import Optional

from platformdirs import user_config_dir
from typer import Argument, BadParameter, Context, Exit, Option, Typer

DEFAULT = {
    "_app": {"name": "alcli", "author": "alwaysdata"},
    "api": {"base_url": "https://api.alwaysdata.com/", "version": "v1", "key": None, "account": None},
    "output": {"pretty": "on", "format": "text"},
}


class Config(ConfigParser):
    def __init__(self, config_file=None, session_dict=None):
        super(Config, self).__init__(
            allow_no_value=True,
        )
        self._config_file = config_file
        self.read_session(session_dict)
        self.reload()

    def read_session(self, session_dict=None):
        if not hasattr(self, "_session"):
            self._session = collections.defaultdict(dict)

        if session_dict is not None:
            for key, value in session_dict.items():
                section, option = key.split("_", 1)
                self._session[section][option] = value

    def reload(self, force=False):
        self.read(self._get_config_file_path())
        # Load default sections if they don't exist in the config file
        # Otherwise, the fallback mecanism will always take precedence (`configparser.NoSectionError`)
        for section in DEFAULT.keys():
            if not self.has_section(section):
                self.add_section(section)

    def _get_config_file_path(self):
        """
        Return a Path to the config.ini file on the filesystem.
        """
        if self._config_file is None:
            config_dir_path = user_config_dir(self.get("_app", "name"), self.get("_app", "author"), roaming=True)
            self._config_file = Path(f"{config_dir_path}/config.ini")
        return self._config_file

    def write(self):
        """
        Persist the configuration changes in the filesystem.
        """
        to_save = ConfigParser()
        to_save.read_dict(self)

        # Remove empty and hidden sections
        for section in self.sections():
            if section.startswith("_") or not len(self.options(section)):
                to_save.remove_section(section)

        config_path = self._get_config_file_path()
        config_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)

        with open(config_path, "w") as config_file:
            to_save.write(config_file)

    def _get_session_section(self, section):
        return self._session.get(section, {})

    def _get_fallback_option(self, section, option):
        return DEFAULT.get(section, {}).get(option, None)

    def get(self, *args, **kwargs):
        return super(Config, self).get(
            *args,
            vars=self._get_session_section(args[0]),
            fallback=self._get_fallback_option(args[0], args[1]),
            **{k: v for k, v in kwargs.items() if k not in ("vars", "fallback")},
        )

    def getint(self, *args, **kwargs):
        return super(Config, self).getint(
            *args,
            vars=self._get_session_section(args[0]),
            fallback=self._get_fallback_option(args[0], args[1]),
            **{k: v for k, v in kwargs.items() if k not in ("vars", "fallback")},
        )

    def getfloat(self, *args, **kwargs):
        return super(Config, self).getfloat(
            *args,
            vars=self._get_session_section(args[0]),
            fallback=self._get_fallback_option(args[0], args[1]),
            **{k: v for k, v in kwargs.items() if k not in ("vars", "fallback")},
        )

    def getboolean(self, *args, **kwargs):
        return super(Config, self).getboolean(
            *args,
            vars=self._get_session_section(args[0]),
            fallback=self._get_fallback_option(args[0], args[1]),
            **{k: v for k, v in kwargs.items() if k not in ("vars", "fallback")},
        )


_config = None


def load(config_file=None, session_dict=None):
    global _config
    if _config is None:
        _config = Config(config_file, session_dict)
    else:
        _config.read_session(session_dict)
    return _config


from .utils.console import Renderer, print

app = Typer()


def list_callback(lock: bool):
    """
    List available config options
    """
    if lock:
        content = {
            section: [option for option in DEFAULT[section].keys() if not option.startswith("_")]
            for section in DEFAULT.keys()
            if not section.startswith("_")
        }
        print(content, title="Available config options", renderer=Renderer.tree)
        raise Exit


@app.callback()
def main(
    list: Optional[bool] = Option(
        None, "--list", callback=list_callback, is_eager=False, help="List available config keys."
    ),
):
    """
    Manage the CLI configuration.

    Use the get and set commands to persists config.

    Examples:

    Read the version of the API use to perform requests:

        $ alwaysdata config get api.version

    Set the account onto which perform requests to `superman`

        $ alwaysdata config set api.account superman
    """
    # Ensure the store is loaded before running `config` commands
    load()


@app.command()
def get(name: str = Argument(..., help="The name of the option to get.")):
    """
    Return the value of the name (<section>.<key>) in the config.
    """
    section, _, name = name.partition(".")
    value = _config.get(section, name, fallback="")
    print(str(value), title=f"{section} {name}")


@app.command()
def set(
    name: str = Argument(..., help="The name of the option to set."),
    value: str = Argument(None, help="The value to set the option to."),
    unset: bool = Option(False, "--unset", help="Remove the option in config."),
    silent: bool = Option(False, help="Do not output value as set feedback."),
):
    """
    Save the value for a name (<section>.<key>) in the config.
    """
    section, _, option = name.partition(".")

    if unset:
        if _config.has_option(section, option):
            _config.remove_option(section, option)

    else:
        if value is None:
            raise BadParameter("Missing argument 'VALUE'")
        if not _config.has_section(section):
            _config.add_section(section)
        _config[section][option] = value

    _config.write()

    if not silent and not unset:
        get(name)
