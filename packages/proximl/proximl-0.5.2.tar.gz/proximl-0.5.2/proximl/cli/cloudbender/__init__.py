import click
from webbrowser import open as browse
from proximl.cli import cli, pass_config, search_by_id_name


@cli.group()
@pass_config
def cloudbender(config):
    """proxiML CloudBender™ commands."""
    pass


from proximl.cli.cloudbender.provider import provider
from proximl.cli.cloudbender.region import region
from proximl.cli.cloudbender.node import node
from proximl.cli.cloudbender.device import device
from proximl.cli.cloudbender.datastore import datastore
from proximl.cli.cloudbender.reservation import reservation
