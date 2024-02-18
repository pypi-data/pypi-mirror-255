import click
import uvicorn
import uvicorn.config

from poaster.__about__ import __version__


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="poaster")
@click.option(
    "--host",
    type=str,
    default="127.0.0.1",
    help="Bind socket to this host.",
    show_default=True,
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="Bind socket to this port.",
    show_default=True,
)
@click.option(
    "--log-level",
    type=click.Choice(list(uvicorn.config.LOG_LEVELS.keys())),
    default="info",
    help="Log level.",
    show_default=True,
)
def poaster(host: str, port: int, log_level: str) -> None:
    """Launches the application server."""
    uvicorn.run("poaster.app:app", host=host, port=port, log_level=log_level)
