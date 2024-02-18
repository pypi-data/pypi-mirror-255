from typing import Optional

import typer
from rich.console import Console
from typing_extensions import Annotated

import mcloud.auth as marimo_auth
import mcloud.publish as marimo_publish
from mcloud.constants import state
from mcloud.errors import catch_exception
from mcloud.generated.core.api_error import ApiError
from mcloud.logger import LOG
from mcloud.resources.resources import ApplicationsResource

console = Console()
# Create the main app
app = typer.Typer(
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
)
# Create the applications app
applications_app = typer.Typer(
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
)
app.add_typer(applications_app, name="applications")
# Create the auth app
auth_app = typer.Typer(
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
)
app.add_typer(auth_app, name="auth")

__version__ = "0.2.1"


@app.command()
def version():
    console.print(__version__)


@app.command()
@catch_exception(ApiError)
@catch_exception(Exception)
@catch_exception(KeyboardInterrupt)
def login():
    marimo_auth.login()


@app.command()
@catch_exception(ApiError)
@catch_exception(Exception)
@catch_exception(KeyboardInterrupt)
def publish(
    path: Annotated[
        str, typer.Argument(..., help="Path to the directory to publish")
    ] = ".",
    dryrun: Annotated[bool, typer.Option(help="Dry run")] = False,
    token: Annotated[
        Optional[str],
        typer.Option(
            help="Marimo token to use, otherwise use the one in config"
        ),
    ] = None,
    image: Annotated[
        Optional[str],
        typer.Option(help="Docker image to use for publishing"),
    ] = None,
    api_url: Annotated[
        Optional[str],
        typer.Option(help="Marimo API URL to use"),
    ] = None,
    config: Annotated[
        Optional[str],
        typer.Option(
            "--config",
            "-c",
            help="Path to the mcloud.*.toml configuration file to use instead. Defaults to mcloud.toml in the path",
        ),
    ] = None,
):
    marimo_publish.publish(
        path=path,
        config_path=config,
        dryrun=dryrun,
        token=token,
        image=image,
        api_url=api_url,
    )


@applications_app.command("list")
@catch_exception(ApiError)
@catch_exception(Exception)
@catch_exception(KeyboardInterrupt)
def applications_list(
    token: Annotated[
        Optional[str],
        typer.Option(
            help="Marimo token to use, otherwise use the one in config"
        ),
    ] = None,
    api_url: Annotated[
        Optional[str],
        typer.Option(help="Marimo API URL to use"),
    ] = None,
    organization: Annotated[
        Optional[str],
        typer.Option(help="Organization slug to use"),
    ] = None,
):
    resource = ApplicationsResource(
        token=token,
        api_url=api_url,
        organization_slug=organization,
    )

    resource.list()


@applications_app.command("get")
@catch_exception(ApiError)
@catch_exception(Exception)
@catch_exception(KeyboardInterrupt)
def applications_get(
    app_id: Annotated[
        str,
        typer.Argument(..., help="Application ID to get"),
    ],
    token: Annotated[
        Optional[str],
        typer.Option(
            help="Marimo token to use, otherwise use the one in config"
        ),
    ] = None,
    api_url: Annotated[
        Optional[str],
        typer.Option(help="Marimo API URL to use"),
    ] = None,
):
    resource = ApplicationsResource(
        token=token,
        api_url=api_url,
    )

    resource.get(app_id)


@app.command()
@catch_exception(ApiError)
@catch_exception(Exception)
@catch_exception(KeyboardInterrupt)
def logout():
    marimo_auth.logout()


@auth_app.command("token")
@catch_exception(ApiError)
@catch_exception(Exception)
@catch_exception(KeyboardInterrupt)
def auth_token():
    print(marimo_auth.get_access_token())


@app.callback()
@catch_exception(ApiError)
@catch_exception(Exception)
@catch_exception(KeyboardInterrupt)
def main(verbose: bool = False, interactive: bool = True):
    if verbose:
        LOG.debug("Will write verbose output")
        LOG.setLevel("DEBUG")
        state["verbose"] = True

    if not interactive:
        LOG.debug("Will not prompt for missing configuration values")
        state["interactive"] = False


if __name__ == "__main__":
    app()
