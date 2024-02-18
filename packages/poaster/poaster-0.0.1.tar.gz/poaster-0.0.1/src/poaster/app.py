from fastapi import FastAPI

from poaster.__about__ import __version__


def get_app() -> FastAPI:
    """Build and configure application server."""

    app = FastAPI(
        docs_url="/api/v1/docs",
        title="poaster",
        version=__version__,
        summary="Minimal, libre bulletin board for posting announcements.",
        license_info={
            "name": "GNU Affero General Public License (AGPL)",
            "url": "https://www.gnu.org/licenses/agpl-3.0.html",
        },
    )

    return app


app = get_app()
