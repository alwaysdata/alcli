# alcli

CLI client for alwaysdata customers operations purposes.

## Pre-requisites

The project relies on Python 3.11 and [Nuitka](https://nuitka.net/) for its build / distribution process.
It uses [Poetry](https://python-poetry.org/) and [PoeThePoet](https://poethepoet.natn.io/) to ensure the development workflow.

For local build purposes, you'll also need [patchelf](https://github.com/NixOS/patchelf), [clang](https://clang.llvm.org/), and [upx](https://upx.github.io/).

## Development

### Install environment

1. Check that Poetry is properly installed and install it otherwise:

   ```sh
   $ which poetry || curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:

   ```sh
   $ poetry self add 'poethepoet[poetry_plugin]'
   $ poetry install
   ```

### Running the project

Poetry declares an `alwaysdata` command that runs the `__main__` script. The name is choosen after the expacted name of the CLI when distributed.

To run the CLI, call it with Poetry:

```sh
$ poetry run alwaysdata --help
```

Top-level tasks are handled with PoeThePoet in the `pyproject.toml` file, under the package name (`alcli`) as top-level command. You can run:

```sh
$ poetry alcli format   # format source and test files
$ poetry alcli test     # run tests
$ poetry alcli build    # build a distributable asset
```

Run the `poetry alcli` command for an exhaustive list of supported commands.

### Architecture

The project heavily relies on [Typer](https://typer.tiangolo.com/) as its "frontend" framework for CLI commands.

The main command, as well as the Typer `app` instance, lives in the `src/alcli.py` file.

Every sub-commands (`config`, `auth`, `site`, etc.) are dedicated [Typer sub-apps commands](https://typer.tiangolo.com/tutorial/subcommands/) living in their dedicated modules in `src`.

The `src/utils` package contains useful wrapper for *api calls* or console `print`*ing*, as we allow users to select the kind of feedback they want on stdout (`json` or `plain-text`, with or without theming, etc). Subcommands must rely on those utils to enforce a consistent user experience at last.

#### Example: adding a new sub-command module

We'll add a new `my` module which will exposes a `endpoint` sub-command, returning an arbitrary endpoint (namely `my-endpoint`) at the API.

Add a new `src/my.py` file with:

```py
from typer import Typer

from .utils.api import api_url
from .utils.console import print

URI = "my-endpoint"

app = Typer()


@app.callback()
def my():
    """
    Example sub-command module
    """


@app.command()
def endpoint():
    """
    Display an arbitrary API url
    """
    uri = api_url(URI)

    print(str(uri), title="My-endpoint example")
```

Then in `src/alcli.py`, registrer this new sub-commands module:

```py
from .my import app as my_app

#...

app.add_typer(my_app, name="my")
```

Finally, test it by calling it in your terminal:

```sh
$ poetry run alwaysdata my endpoint
╭─ My-endpoint example ──────────────────────────────────────────────────────╮
│ https://api.alwaysdata.com//v1/my-endpoint/                                │
╰────────────────────────────────────────────────────────────────────────────╯
```

## Build

The build process is handled by Nuitka, with a few options tweaked in the build command living in the build task.

### Local build

To produce a local build, run `poetry alcli build`. It will produce a `./tmp/alwaysdata` single file containing an auto-extractable archive ready to be run on *the very same architecture as the current host*. You can test it with `./tmp/alwaysdata --help` to check it.

### Distributed builds

Since the project lives in Github, it takes advantage of [Github Workflows](https://docs.github.com/en/actions/using-workflows) to build artifacts for all supported platforms (Windows, MacOS, Linux). Check the `.github/workflows/build.yml` for an overview of the distributed build process.

## Distribution

Artifacts compiled per platforms through Github Workkflows are available in the [Actions: Build](https://github.com/alwaysdata/alcli/actions/workflows/build.yml) section of the project. Select the related commit. Artifacts are located at the bottom of the page.
