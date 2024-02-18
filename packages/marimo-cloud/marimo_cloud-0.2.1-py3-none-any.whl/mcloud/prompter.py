import os
import sys
from typing import Callable, List, Optional, TypeVar

import inquirer
from rich.console import Console
from rich.prompt import Confirm, Prompt

from mcloud.constants import state
from mcloud.logger import LOG

console = Console()

T = TypeVar("T")


def select(
    message: str,
    items: List[T],
    to_display: Optional[Callable[[T], str]] = None,
) -> T:
    """
    Prompt user to select an item from a list of items.

    Wraps inquirer.prompt() to provide a simple interface for selecting an item
    while preserving the whole item instead of just the item's name.
    """

    def _to_display(item: T) -> str:
        return str(item)

    if not to_display:
        to_display = _to_display

    choices = [to_display(item) if to_display else item for item in items]
    verify_unique = len(choices) == len(set(choices))
    if not verify_unique:
        raise ValueError("Items must be unique")

    answers = inquirer.prompt(
        [
            inquirer.List(
                "item",
                message=message,
                choices=choices,
            )
        ],
        raise_keyboard_interrupt=True,
    )

    answer = answers["item"]
    item = next((item for item in items if to_display(item) == answer), None)
    return item


def confirm(message: str, default: bool = False) -> bool:
    """
    Prompt user to confirm an action.
    """

    if not _is_interactive():
        LOG.debug(f"Skipping confirmation: {message}")
        return True

    return Confirm.ask(message, default=default)


def text(message: str, default: Optional[str] = None) -> str:
    """
    Prompt user to enter text.
    """

    if not _is_interactive():
        LOG.debug(f"Skipping text prompt: {message}")
        if not default:
            raise ValueError("Text prompt requires a default value")
        return default

    return Prompt.ask(message, default=default)


def slug(message: str, default: Optional[str] = None) -> str:
    """
    Prompt user to enter a slug.
    """

    def _slugify(text: str) -> str:
        return text.lower().replace(" ", "-").replace("_", "-")

    if not _is_interactive():
        LOG.debug(f"Skipping slug prompt: {message}")
        if not default:
            raise ValueError("Slug prompt requires a default value")
        return _slugify(default)

    answer = Prompt.ask(
        message, default=_slugify(default) if default else None
    )
    return answer


def _is_interactive() -> bool:
    """
    Check if the current process is interactive.
    """
    process_interactive = bool(os.isatty(sys.stdin.fileno()))
    # If process is not interactive, return
    if not process_interactive:
        return False
    # Otherwise, check state
    return state["interactive"]
