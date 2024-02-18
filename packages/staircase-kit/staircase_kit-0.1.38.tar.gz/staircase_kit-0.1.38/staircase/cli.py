import os
import click

from .config import DATA_FOLDER, VAR_FOLDER, CONFIG_FILE_PATH

from .commands.postman import postman_group
from .commands.envs import envs_group
from .commands import config as config_
from .commands import ci
from .commands import asana
from .commands import health


def get_cli():
    cli = click.Group()
    cli.add_command(postman_group)
    cli.add_command(envs_group)
    cli.add_command(config_.group)
    cli.add_command(ci.command)
    cli.add_command(asana.group)
    cli.add_command(health.health_group)
    return cli


def init_cli():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    if not os.path.exists(VAR_FOLDER):
        os.makedirs(VAR_FOLDER)

    if not os.path.exists(CONFIG_FILE_PATH):
        CONFIG_FILE_PATH.parent.mkdir(exist_ok=True, parents=True)


    cli = get_cli()
    return cli

def launch_cli():
    cli = init_cli()
    cli()


