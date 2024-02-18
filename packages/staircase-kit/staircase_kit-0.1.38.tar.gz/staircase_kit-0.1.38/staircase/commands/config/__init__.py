import click

from . import setup
from . import file_path

@click.group(name="config")
def group():
    ...

group.add_command(setup.command)
group.add_command(file_path.command)