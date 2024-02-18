import rich
import click

from staircase.lib.click import async_cmd
from staircase.env_storage import EnvironmentStorage, Env
from staircase.command_providers import  env_storage_provider


@click.command(name="add")
@click.option("--domain", prompt="Env domain name")
@click.option("--api-key", prompt="Api key")
@env_storage_provider()
@async_cmd
async def command( env_storage: EnvironmentStorage, domain: str, api_key: str, **_):
    env = Env(domain_name=domain, api_key=api_key)
    env_storage.add_env(env)
    rich.print("[green]Imported.")
