import asyncio
import click
import logging
from os import devnull
from sys import stderr, stdout


from proximl.proximl import ProxiML


class ProxiMLRunner(object):
    def __init__(self):
        self._proximl_client = None

    @property
    def client(self) -> ProxiML:
        if self._proximl_client is None:
            try:
                self._proximl_client = ProxiML()
            except Exception as err:
                raise click.UsageError(err)
        return self._proximl_client

    async def _run(self, *tasks):
        return await asyncio.gather(*tasks)

    def run(self, *tasks):
        try:
            if len(tasks) == 1:
                return_value = asyncio.run(*tasks)
            else:
                return_value = asyncio.run(self._run(*tasks))
        except Exception as err:
            raise click.UsageError(err)
        return return_value


class Config(object):
    def __init__(self):
        self.stderr = stderr
        self.stdout = stdout
        self.proximl = ProxiMLRunner()


def search_by_id_name(term, list):
    found = None
    for item in list:
        if item.id == term:
            found = item
            break
    if None is found:
        for item in list:
            try:
                if item.name == term:
                    found = item
                    break
            except AttributeError:
                break
    return found


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.version_option(package_name="proximl", prog_name="proxiML CLI and SDK")
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Show debug output.",
)
@click.option(
    "--output-file",
    "-o",
    type=click.File("w"),
    default="-",
    help="Send output to file.",
)
@click.option(
    "--silent",
    "-s",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Silence all output.",
)
@click.option(
    "--verbose",
    "-v",
    "verbosity",
    count=True,
    type=click.INT,
    default=0,
    help="Specify verbosity (repeat to increase).",
)
@pass_config
def cli(config, debug, output_file, silent, verbosity):
    """proxiML command-line interface."""
    config.stdout = output_file

    if debug or verbosity > 0:
        if silent:
            click.echo(
                "Ignoring silent flag when debug or verbosity is set.",
                file=config.stderr,
            )
        if verbosity == 1:
            verbosity = logging.INFO
        else:
            verbosity = logging.DEBUG
    elif silent:
        config.stderr = config.stdout = open(devnull, "w")
    else:
        verbosity = logging.WARNING

    if verbosity != logging.WARNING:  # default
        click.echo(
            f"Verbosity set to {logging.getLevelName(verbosity)}",
            file=config.stderr,
        )

    logging.basicConfig(
        format="%(asctime)s.%(msecs)03dZ  %(levelname)s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=verbosity,
        stream=config.stderr,
        force=True,
    )


@cli.command()
@pass_config
def configure(config):
    active_project_id = config.proximl.client.active_project
    projects = config.proximl.run(config.proximl.client.projects.list())
    project_names = [project.name for project in projects]

    active_project = [
        project for project in projects if project.id == active_project_id
    ]

    active_project_name = (
        active_project[0].name if len(active_project) else "UNSET"
    )

    click.echo(f"Current Active Project: {active_project_name}")

    name = click.prompt(
        "Select Active Project:",
        type=click.Choice(project_names, case_sensitive=True),
        show_choices=True,
        default=active_project_name,
    )
    selected_project = [
        project for project in projects if project.name == name
    ]
    config.proximl.client.set_active_project(selected_project[0].id)


from proximl.cli.connection import connection
from proximl.cli.dataset import dataset
from proximl.cli.model import model
from proximl.cli.checkpoint import checkpoint
from proximl.cli.environment import environment
from proximl.cli.gpu import gpu
from proximl.cli.job import job
from proximl.cli.project import project
from proximl.cli.cloudbender import cloudbender
