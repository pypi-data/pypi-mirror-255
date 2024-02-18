import rich
import click

from staircase.lib.click import async_cmd
from staircase.env_storage import EnvironmentStorage 
from staircase.command_providers import env_storage_provider
from staircase.lib.fzf import prompt


@click.command(name="remove")
@env_storage_provider()
@async_cmd
async def command( env_storage: EnvironmentStorage, **_):
    envs = env_storage.get_all_envs()
    envs_to_delete = prompt([ f"{index} - {env.domain_name}:{env.api_key}" for index, env in enumerate(envs) ])
    for env_to_delete in envs_to_delete:
        index = int(env_to_delete.split('-')[0])
        env_storage.remove_env(index)

    rich.print("[green]Removed.")
