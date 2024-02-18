import click

from . import api
from . import envs

@click.group(name="import")
def group():
    ...

group.add_command(api.command)
group.add_command(envs.command)