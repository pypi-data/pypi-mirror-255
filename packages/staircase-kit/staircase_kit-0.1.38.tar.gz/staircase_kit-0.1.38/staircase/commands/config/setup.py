from rich.prompt import Prompt
import click

from staircase.lib.click import async_cmd
from staircase.config import write_user_cfg, get_user_cfg


@click.command(name="setup")
@async_cmd
async def command():
    """
    Easy setup of all variables.
    """
    user_config = get_user_cfg()
    user_config.postman_api_key = Prompt.ask("Postman api key", default=user_config.postman_api_key)
    user_config.marketplace_api_key = Prompt.ask("Marketplace api key", default=user_config.marketplace_api_key)
    user_config.github_token = Prompt.ask("Github token. With authorized github cli", default=user_config.github_token)
    user_config.asana_token = Prompt.ask("Asana token", default=user_config.asana_token)
    write_user_cfg(user_config)
