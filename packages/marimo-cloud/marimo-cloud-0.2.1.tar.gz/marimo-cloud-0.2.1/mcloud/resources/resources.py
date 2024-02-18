from typing import List, Optional

from rich.console import Console

from mcloud import prompter
from mcloud.client import create_marimo_client
from mcloud.constants import LOGIN_URL
from mcloud.generated.resources.marimo_v_1.client import MarimoV1Client
from mcloud.generated.resources.marimo_v_1.errors.organization_not_found_error import (
    OrganizationNotFoundError,
)
from mcloud.generated.resources.marimo_v_1.types.application import (
    Application,
)
from mcloud.generated.resources.marimo_v_1.types.application_id import (
    ApplicationId,
)
from mcloud.generated.resources.marimo_v_1.types.organization import (
    Organization,
)

console = Console()


class Resource:
    def __init__(
        self,
        token: Optional[str] = None,
        api_url: Optional[str] = None,
        dryrun: bool = False,
    ):
        self.client = create_marimo_client(
            token=token, dryrun=dryrun, api_url=api_url
        )


class ApplicationsResource(Resource):
    client: MarimoV1Client

    def __init__(
        self,
        token: Optional[str] = None,
        api_url: Optional[str] = None,
        organization_slug: Optional[str] = None,
    ):
        super().__init__(token=token, api_url=api_url)
        self._organization_slug = organization_slug

    def list(self) -> List[Application]:
        client: MarimoV1Client = self.client
        org = self._get_organization()
        apps = client.list_applications(organization_id=org.organization_id)
        # Pretty print applications
        for app in apps:
            self._print_application(app)

        return apps

    def get(self, app_id: ApplicationId) -> Application:
        client: MarimoV1Client = self.client
        app = client.get_application(application_id=app_id)
        self._print_application(app)
        return app

    def _print_application(self, app: Application) -> None:
        console.print(
            "\n".join(
                [
                    f"[bold]{app.application_id}[/bold] - {app.application_slug}",
                    f"  Last deployed: {app.last_deployment.started_at.isoformat() if app.last_deployment else '...'}",
                    f"  Status: {app.last_deployment.status if app.last_deployment else '...'}",
                    f"  Dashboard: {LOGIN_URL}/dashboard/{app.application_id}",
                    f"  URL: {LOGIN_URL}/@{app.organization_slug}/{app.application_slug}",
                ]
            )
        )

    def _get_organization(self) -> Organization:
        client: MarimoV1Client = self.client
        orgs = client.list_organizations()

        # If no organizations, return
        if len(orgs) == 0:
            console.print("[red]No organizations found[/red]")
            raise OrganizationNotFoundError()

        # If organization slug is provided, select it
        if self._organization_slug:
            selected_org = next(
                (
                    org
                    for org in orgs
                    if org.organization_slug == self._organization_slug
                ),
                None,
            )
            if not selected_org:
                raise OrganizationNotFoundError()
            else:
                return selected_org

        # If only one organization, select it
        if len(orgs) == 1:
            return orgs[0]

        # Select organization
        selected_org = prompter.select(
            "Select organization",
            orgs,
            lambda org: org.organization_slug,
        )

        return selected_org
