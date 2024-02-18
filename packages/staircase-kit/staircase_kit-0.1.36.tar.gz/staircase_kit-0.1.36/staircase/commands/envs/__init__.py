
import click

from . import list
from . import add
from . import remove

@click.group(name="envs")
def envs_group():
    """
    Manage your environments.
    """
    ...

envs_group.add_command(list.command)
envs_group.add_command(add.command)
envs_group.add_command(remove.command)