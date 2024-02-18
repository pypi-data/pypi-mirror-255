import json
import rich
import click
from pydantic.json import pydantic_encoder

from staircase.lib.click import async_cmd
from staircase.env_storage import EnvironmentStorage
from staircase.command_providers import env_storage_provider


@click.command(name="list")
@env_storage_provider()
@async_cmd
async def command( env_storage: EnvironmentStorage, **_):
    rich.print_json(json.dumps(env_storage.get_all_envs(), default=pydantic_encoder))
