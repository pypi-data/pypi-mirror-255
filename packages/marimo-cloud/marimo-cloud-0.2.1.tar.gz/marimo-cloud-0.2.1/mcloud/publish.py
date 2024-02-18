import os
import tarfile
from typing import List, Optional
from urllib.request import Request, urlopen

from rich.console import Console
from rich.status import Status

import mcloud.prompter as prompter
from mcloud.client import create_marimo_client
from mcloud.config import (
    DEFAULT_FILES,
    REQUIRED_FILES,
    AppConfiguration,
    ConfigReader,
)
from mcloud.generated import CreateApplicationRequest
from mcloud.generated.resources.marimo_v_1.client import MarimoV1Client
from mcloud.generated.resources.marimo_v_1.errors.missing_fields_error import (
    MissingFieldsError,
)
from mcloud.generated.resources.marimo_v_1.types.deployment import (
    Deployment,
)
from mcloud.logger import LOG

console = Console()

ASSETS_NAME = "app_source.tar.gz"


def read_app_py(path: str) -> str:
    """
    Read app.py from current directory

    TODO: make location configurable
    """
    try:
        file_path = os.path.join(os.getcwd(), path, "app.py")
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        directory = os.path.join(os.getcwd(), path)
        raise MissingFieldsError(
            [f"app.py not found in {directory}"]
        ) from None


def read_requirements_txt(path: str) -> str:
    """
    Read requirements.txt from current directory

    TODO: make location configurable
    """
    try:
        file_path = os.path.join(os.getcwd(), path, "requirements.txt")
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def publish(
    path: str,
    dryrun: bool,
    config_path: Optional[str],
    token: Optional[str],
    image: Optional[str],
    api_url: Optional[str],
) -> None:
    """
    Publish current directory to Marimo
    """
    LOG.debug("Publishing to marimo cloud at %s", path)

    # Create client
    client = create_marimo_client(token=token, dryrun=dryrun, api_url=api_url)
    # Read app config
    config_reader = ConfigReader(path, config_path, dryrun)
    app_config = config_reader.read_app_config()

    # If no app id, ask to link app
    if not app_config.app_id:
        # Ask to link app or create new
        link_or_new = prompter.select(
            "No application linked. Would you like to link an existing application or create a new one?",
            ["Link existing", "Create new", "Cancel"],
        )

        # If cancel, exit
        if link_or_new == "Cancel":
            return
        # If link existing, ask for app id
        elif link_or_new == "Link existing":
            # Select organizations
            orgs = client.list_organizations()
            if len(orgs) == 0:
                console.print("[red]No organizations found[/red]")
                return
            selected_org = prompter.select(
                "Select organization",
                orgs,
                lambda org: org.organization_slug,
            )

            # Select app
            apps = client.list_applications(
                organization_id=selected_org.organization_id
            )
            if len(apps) == 0:
                console.print("[red]No applications found[/red]")
                return
            selected_app = prompter.select(
                "Select application",
                apps,
                lambda app: f"{app.name} ({app.application_slug})",
            )
        # If create new, ask for app name
        elif link_or_new == "Create new":
            # Select organizations
            orgs = client.list_organizations()
            if len(orgs) == 0:
                console.print("[red]No organizations found[/red]")
                return
            selected_org = prompter.select(
                "Select organization",
                orgs,
                lambda org: org.organization_slug,
            )

            # Ask for app name
            app_name = prompter.text("Enter a name for your application")

            # Ask for app slug
            app_slug = prompter.slug(
                "Enter a slug for your application", default=app_name
            )

            # Create app
            selected_app = client.create_application(
                request=CreateApplicationRequest(
                    application_slug=app_slug,
                    name=app_name,
                    organization_id=selected_org.organization_id,
                )
            )
        else:
            raise Exception("Invalid option selected")

        # Save app id
        app_config.app_id = selected_app.application_id
        app_config.app_slug = selected_app.application_slug
        config_reader.write_app_config(app_config)

    else:
        # Load app
        app = client.get_application(application_id=app_config.app_id)

        # If slug doesn't match, write new slug its only used for display
        if app.application_slug != app_config.app_slug:
            app_config.app_slug = app.application_slug
            config_reader.write_app_config(app_config)

        # Confirm app
        confirm = prompter.confirm(
            f"Deploy application [cyan bold]{app.application_slug}[/cyan bold]?"
        )

        if not confirm:
            return

    with console.status(
        f"[cyan]Deploying [bold]{app_config.app_slug}[/bold]...[/cyan]"
    ) as status:
        # Start deployment
        try:
            if image:
                response = _create_deployment_by_image(
                    client, app_config, image
                )
            else:
                response = _create_deployment_by_source_code(
                    client, path, app_config, status
                )
            # TODO: link to deployment when we support that page
            deployment_url = f"https://marimo.io/dashboard/applications/{response.application_id}"
            console.print("[green]Application deployment started![/green]")
            console.print(
                f"View can track your deployment at [cyan]{deployment_url}[/cyan]"
            )
        except Exception as e:
            console.print(f"[red]Error deploying application: {e}[/red]")
            raise e


# 30MB
MAX_UPLOAD_SIZE = 30 * 1024 * 1024


def _create_deployment_by_source_code(
    client: MarimoV1Client,
    path: str,
    app_config: AppConfiguration,
    status: Status,
) -> Deployment:
    """
    Create a deployment by source code
    """
    code = read_app_py(path)
    requirements = read_requirements_txt(path)

    # Required files are the app entrypoint or app.py
    required_files = (
        [app_config.app_entrypoint]
        if app_config.app_entrypoint
        else REQUIRED_FILES
    )

    included_files = app_config.files or DEFAULT_FILES

    # Add all required files to included files
    for file in required_files:
        if file not in included_files:
            included_files.append(file)

    assets = _tar_assets(path, included_files, required_files)

    assert app_config.app_id is not None

    version: Optional[str] = None
    # If assets are > 30mb ask to confirm, and use a signed url
    size = os.path.getsize(ASSETS_NAME)
    if size > MAX_UPLOAD_SIZE:
        status.stop()
        pretty_size = round(size / (1024 * 1024), 2)
        confirm = prompter.confirm(
            f"Your included files are {pretty_size}MB in size, "
            + "it will take some time to upload. Do you want to continue?"
        )
        if not confirm:
            raise Exception("Deployment cancelled")

        upload_url_response = client.create_upload_url(
            application_id=app_config.app_id,
        )
        version = upload_url_response.version

        # Upload assets
        with open(ASSETS_NAME, "rb") as f:
            console.print("Uploading assets...")
            upload_response = urlopen(
                Request(
                    url=upload_url_response.url,
                    data=f.read(),
                    method="PUT",
                    headers={"Content-Type": "application/octet-stream"},
                )
            )
            if upload_response.status != 200:
                console.print("Error uploading assets")
                raise Exception(
                    "Error uploading assets", upload_response.status
                )
            else:
                # Set assets to an empty file
                assets = open("/dev/null", "rb")
                console.print("Continuing deployment...")
                status.update("Creating deployment...")

    # Create deployment
    try:
        response = client.create_deployment(
            application_id=app_config.app_id,
            code=code,
            requirements_txt=requirements,
            assets=assets,
            version=version,
            cli_flags=app_config.cli_flags,
            app_entrypoint=app_config.app_entrypoint,
            python_version=app_config.python_version,
        )
    finally:
        # delete tar file
        assets.close()
        os.remove(ASSETS_NAME)

    return response


def _create_deployment_by_image(
    client: MarimoV1Client,
    app_config: AppConfiguration,
    image: str,
) -> Deployment:
    """
    Create a deployment by image
    """
    assert app_config.app_id is not None

    # Create deployment
    response = client.create_deployment_with_image(
        application_id=app_config.app_id,
        image=image,
    )

    return response


def _tar_assets(
    path: str,
    files: List[str],
    required_files: List[str],
) -> tarfile.TarFile:
    """
    Tar all the assets in the current directory and return the tar file.
    """

    # Validate files
    missing_files: List[str] = []
    for file in files:
        file_path = os.path.join(os.getcwd(), path, file)
        if not os.path.exists(file_path) and file in required_files:
            missing_files.append(f"Required file {file} not found")

    if len(missing_files) > 0:
        raise MissingFieldsError(missing_files)

    # Create tar file
    tar = tarfile.open(ASSETS_NAME, "w:gz")
    for file in files:
        file_path = os.path.join(os.getcwd(), path, file)
        if not os.path.exists(file_path):
            continue
        tar.add(file_path, arcname=os.path.join("app_source", file))

    # Close tar file
    tar.close()

    # Return tar file
    return open(ASSETS_NAME, "rb")
