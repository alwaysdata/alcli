from typing import Any, Callable, Optional, Union

from click import Command, get_current_context
from typer.main import Typer, get_command_from_info
from typer.models import CommandInfo


def find_command_info(
    typer_instance: Typer, callback: Callable
) -> Optional[CommandInfo]:
    for command_info in typer_instance.registered_commands:
        if command_info.callback == callback:
            return command_info
    for group in typer_instance.registered_groups:
        command_info = find_command_info(group.typer_instance, callback)
        if command_info:
            return command_info
    return None


def callback_to_click_command(
    typer_instance: Typer,
    callback: Union[Callable, Command],
) -> Union[Callable, Command]:
    command_info = find_command_info(typer_instance, callback)
    if command_info:
        callback = get_command_from_info(
            command_info,
            pretty_exceptions_short=typer_instance.pretty_exceptions_short,
            rich_markup_mode=typer_instance.rich_markup_mode,
        )
    return callback


def invoke(
    typer_instance: Typer, callback: Union[Callable, Command], *args, **kwargs
) -> Any:
    ctx = get_current_context()
    return ctx.invoke(
        callback_to_click_command(typer_instance, callback), *args, **kwargs
    )


def forward(
    typer_instance: Typer, callback: Union[Callable, Command], *args, **kwargs
) -> Any:
    ctx = get_current_context()
    return ctx.forward(
        callback_to_click_command(typer_instance, callback), *args, **kwargs
    )
