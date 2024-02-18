from typing import Optional
import rich
import subprocess
import click
import click
from staircase.config import UserConfig
from staircase.lib.click import async_cmd

from staircase.command_providers import (
    env_manager_provider,
    staircase_provider,
    user_config_provider,
    env_storage_provider,
    EnvironmentStorage,
)
from staircase.env_manager import EnvironmentManager

from staircase.lib.fzf import prompt_numbered, prompt
from staircase.lib.click import async_cmd
from staircase.lib.sdk.staircase_env import StaircaseEnvironment
from staircase.staircase import Staircase
from staircase.lib.sdk.ci import clone, build, deploy
from staircase.user_prompts import select_product_git_repo


@click.command(
    "set_health_check",
)
@click.option(
    "--product",
    "-p",
    help="Product name in marketplace.",
)
@click.option(
    "--target",
    "-t",
    help="Target domain of environment.",
)
@click.option("--disable", "-d", help="By default it enables.", flag_value=True)
@env_manager_provider()
@staircase_provider()
@user_config_provider()
@env_storage_provider()
@async_cmd
async def command(
    *,
    product,
    target,
    disable: bool,
    staircase: Staircase,
    env_manager: EnvironmentManager,
    env_storage: EnvironmentStorage,
    user_config: UserConfig,
):
    products = await staircase.get_all_product_components()
    if not product:
        product = prompt_numbered(products, transform=lambda e: e["product_name"])

        envs = env_storage.get_all_envs()
        env_names = [env.domain_name for env in envs]
        selected_env = prompt(env_names, header="Select env to deploy...")
        if selected_env:
            target = selected_env[0]

    env: Optional[StaircaseEnvironment] = env_manager.get_staircase_env(target)
    is_disabled = True if disable else False
    response = await staircase.toggle_health_check_for_product(
        env, product["product_id"], is_disabled
    )
    print(await response.json())
