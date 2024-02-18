import click

from . import import_

@click.group(name="postman")
def postman_group():
    ...

postman_group.add_command(import_.group)