import os
from typing import List, Optional

import toml
from pydantic import BaseModel
from rich.console import Console

from mcloud.generated.resources.marimo_v_1.types.application_id import (
    ApplicationId,
)
from mcloud.logger import LOG

console = Console()

_CREDENTIALS_FILE = "~/.marimo/credentials.toml"

DEFAULT_FILES = ["app.py", "requirements.txt", "inputs", "input", "layouts"]
REQUIRED_FILES = ["app.py"]


class Credentials(BaseModel):
    created_at: Optional[int]
    expires_at: Optional[int]
    access_token: Optional[str]
    email: Optional[str]


class AppConfiguration(BaseModel):
    """Application configuration.

    **Keys.**

    - `app_id`: application ID
    - `app_slug`: application slug
    - `files`: files to include with the application
        Defaults to `app.py`, `requirements.txt`, `inputs`, `input`, `layouts`
    - `app_entrypoint`: the entrypoint to the application
        Defaults to `app.py`
    - `python_version`: Python version to use
        Defaults to `3.10`
    - `cli_flags`: flags to pass to the CLI
    """

    app_id: Optional[ApplicationId]
    app_slug: Optional[str]

    files: Optional[List[str]]

    app_entrypoint: Optional[str]
    python_version: Optional[str]
    cli_flags: Optional[str]


def read_credentials() -> Credentials:
    """
    Read credentials from the credentials file.
    """
    path = os.path.expanduser(_CREDENTIALS_FILE)
    try:
        with open(path, "r") as file:
            data = toml.load(file)
            return Credentials(**data)
    except FileNotFoundError:
        return Credentials()


def write_credentials(credentials: Credentials) -> None:
    """
    Write credentials to the credentials file.
    """
    path = os.path.expanduser(_CREDENTIALS_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as file:
        toml.dump(credentials.dict(), file)


def delete_credentials() -> None:
    """
    Delete the credentials file.
    """
    path = os.path.expanduser(_CREDENTIALS_FILE)
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


class ConfigReader:
    def __init__(self, path: str, config_path: Optional[str], dryrun: bool):
        self.path = path
        # Config path can be overridden by the user
        # Defaults to mcloud.toml in the path
        self.config_path = os.path.normpath(
            config_path or os.path.join(self.path, "mcloud.toml")
        )
        self.dryrun = dryrun

    def read_app_config(self) -> AppConfiguration:
        """
        Read the app configuration from the mcloud.*.toml file.
        """
        file_path = os.path.join(os.getcwd(), self.config_path)
        try:
            with open(file_path, "r") as file:
                data = toml.load(file)
                LOG.debug("Reading app config from %s", file_path)
                return AppConfiguration(**data)
        except FileNotFoundError:
            LOG.debug("No mcloud.toml file found")
            console.print(
                f"No configuration file found at {file_path}.",
            )
            return AppConfiguration()

    def write_app_config(self, config: AppConfiguration) -> None:
        """
        Write the app configuration to the mcloud.*.toml file.
        """
        if self.dryrun:
            return

        path = os.path.join(os.getcwd(), self.config_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as file:
            toml.dump(config.dict(), file)
            LOG.debug("Wrote app config to %s", path)
