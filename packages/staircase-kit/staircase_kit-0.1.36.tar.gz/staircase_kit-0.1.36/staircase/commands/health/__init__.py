
import click

from . import set_health_check

@click.group(name="health")
def health_group():
    """
    Manage your environments.
    """
    ...

health_group.add_command(set_health_check.command)