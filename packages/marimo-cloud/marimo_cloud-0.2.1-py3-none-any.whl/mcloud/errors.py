from functools import wraps
from typing import Any, Callable, Type

import typer
from rich.console import Console

console = Console()


def catch_exception(
    which_exception: Type[BaseException], exit_code: int = 1
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except which_exception as e:
                error_name = type(e).__name__
                console.print(f"[red]{error_name} {e}[/red]")
                raise typer.Exit(code=exit_code)

        return wrapper

    return decorator
