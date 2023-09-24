import json
from enum import Enum

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from ..config import load


class Format(str, Enum):
    text = "text"
    json = "json"

    def __str__(self):
        return self.value


class Renderer(str, Enum):
    raw = "raw"
    text = "text"
    table = "table"
    card = "card"
    tree = "tree"


console = Console()


def _format(value):
    return "\n".join(value) if type(value) in (list, tuple) else str(value)


def print(content, title=None, no_pretty=False, renderer=Renderer.text, headers=None):
    config = load()
    if config.get("output", "format") == Format.json.value:
        return console.print_json(json.dumps(content))

    pretty = config.getboolean("output", "pretty")
    if no_pretty or renderer is Renderer.raw:
        output = content

    elif renderer is Renderer.text:
        output = Markdown(content)

    elif renderer is Renderer.tree:

        def add_branch(branch, root):
            if type(branch) is dict:
                for name, leaf in branch.items():
                    add_branch(leaf, root.add(name))
            elif type(branch) in (list, tuple):
                for leaf in branch:
                    root.add(leaf)
            else:
                root.add(branch)

        output = Tree(title, hide_root=pretty)
        add_branch(content, output)

    elif renderer is Renderer.card:
        output = Table.grid(padding=(0, 11))
        if headers is not None:
            for key, readable in headers.items():
                output.add_row(f"[b cyan]{readable}", _format(content.get(key, None)))
        else:
            for key, value in content.items():
                output.add_row(f"[b cyan]{key}", _format(value))

    elif renderer is Renderer.table:
        if pretty:
            output = Table(box=box.ROUNDED, leading=True, border_style="dim")
        else:
            output = Table(box=None, safe_box=True)
        if headers is not None:
            for header in headers:
                output.add_column(header)
        for item in content:
            output.add_row(*[_format(value) for value in item.values()])

    if pretty and renderer in (Renderer.card, Renderer.tree, Renderer.text):
        console.print(Panel(output, title=title, title_align="left", box=box.ROUNDED, border_style="dim"))
    else:
        console.print(output)
