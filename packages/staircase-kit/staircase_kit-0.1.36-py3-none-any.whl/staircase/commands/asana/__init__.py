
import click

from . import searches

@click.group(name="asana")
def group():
    ...


group.add_command(searches.command)