from typing import Optional
import rich
import subprocess
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

from staircase.lib.fzf import prompt
from staircase.lib.click import async_cmd
from staircase.lib.sdk.staircase_env import StaircaseEnvironment
from staircase.staircase import Staircase
from staircase.lib.sdk.ci import clone, build, deploy
from staircase.user_prompts import select_product_git_repo

DEFAULT_CI_ENV = "marketplace.staircaseapi.com"


@click.command(
    "ci",
)
@click.argument("actions", type=click.Choice(["clone", "build", "deploy"]), nargs=-1)
@click.option(
    "--bundle-url",
    "-u",
    help="Url of bundle for any step you start your ci from. It will be passed correct to any ci step.",
)
@click.option(
    "--product",
    "-p",
    help="Product name in marketplace. If you dont specify clone, it will be used to get start bundle",
)
@click.option("--repo", "-r", help="Git repo name in Staircase")
@click.option(
    "--type",
    help="Type of bundle can be either service, data, chat or frontend",
    default="service",
    type=click.Choice(["service", "data", "frontend", "chat"]),
)
@click.option(
    "--ci-env",
    "-ci",
    help="Environment where ci products will be called. Ex. mydomain.staircaseapi.com",
)
@click.option("--branch", "-b", help="Branch name of git clone")
@click.option("--verbose", "-v", help="Verbose output", is_flag=True)
@click.option(
    "--target",
    "-t",
    help="Target domain of environment to be deployed. Ex. mydomain.staircaseapi.com",
)
@click.option(
    "--arch",
    help="Arch param of build product",
    default="X86_64",
    type=click.Choice(["X86_64", "ARM64"]),
)
@click.option("--build_env", "-be", help="Build env vars", multiple=True)
@env_manager_provider()
@staircase_provider()
@user_config_provider()
@env_storage_provider()
@async_cmd
async def command(
    *,
    actions,
    bundle_url,
    target,
    type,
    product,
    branch,
    repo,
    build_env,
    arch,
    ci_env: str,
    verbose: bool,
    staircase: Staircase,
    env_manager: EnvironmentManager,
    env_storage: EnvironmentStorage,
    user_config: UserConfig,
):
    """
    Setup your pipeline with clone, assess, test, deploy, build products.

    You can specify steps as arguments, order is not changable. Default order is [clone, build, assess, deploy, test]. If you dont specify any actions if will be [clone, build, deploy]
    """
    if not actions:
        actions = ["clone", "build", "deploy"]

    if not ci_env:
        envs = env_storage.get_all_envs()
        env_names = [env.domain_name for env in envs]
        selected_env = prompt(
            env_names, header="Select ci-env, default = marketplace.staircaseapi.com..."
        )
        if selected_env:
            ci_env = selected_env[0]
        else:
            ci_env = DEFAULT_CI_ENV

    ci_env: Optional[StaircaseEnvironment] = env_manager.get_staircase_env(ci_env)
    if not ci_env:
        raise click.ClickException("CI env is not saved to your envs.")

    # Getting args
    if not user_config.github_token:
        raise click.ClickException("Setup github_token in your config")

    if "clone" in actions:
        if not repo:
            repo = await select_product_git_repo(
                staircase=staircase,
                prompt_header="Select product repo to clone from...",
            )
            if not repo:
                raise click.ClickException("You did not specify any repo")

        if not branch:
            pipe = subprocess.run(
                [
                    "git",
                    "ls-remote",
                    "--heads",
                    f"git@github.com:StaircaseAPI/{repo}.git",
                ],
                stdout=subprocess.PIPE,
                text=True,
            )
            branches = []
            for line in pipe.stdout.splitlines():
                branch = line.split("refs/heads/")[1]
                branches.append(branch)

            branches_selected = prompt(branches, header="Select your branch")

            if not branches_selected:
                raise click.ClickException("You did not specify any branch")

            branch = branches_selected[0]

    if "deploy" in actions and not target:
        envs = env_storage.get_all_envs()
        env_names = [env.domain_name for env in envs]
        selected_env = prompt(env_names, header="Select env to deploy...")
        if selected_env:
            target = selected_env[0]
        if not target:
            raise click.ClickException("Not target env for deploy specified")

    if ["build", "assess", "test"] in actions:
        if not "clone" in actions or not bundle_url:
            raise click.ClickException(
                "You did not specify clone action or bundle_url to start from"
            )

    if (
        "deploy" in actions
        and not bundle_url
        and not ["build", "assess", "test", "clone"]
    ):
        product_names = [
            product["product_name"]
            for product in await staircase.get_all_product_components()
        ]
        products = prompt(product_names)
        if not products:
            raise click.ClickException(
                "No product specified and no bundle_url and no previous action step like clone. Nothing to deploy"
            )
        product_data = staircase.retrieve_product_component(product)
        bundle_url = product_data.get("bundle_url")
        if not bundle_url:
            raise click.ClickException(
                "Selected product does not contain bundle_url in marketplace."
            )

    # Flow
    if verbose:
        rich.print(f"CI_ENV: {ci_env.domain}")
    if "clone" in actions:
        if verbose:
            rich.print(f"Repo: StaircaseCLI/{repo}.git")
            rich.print(f"Branch: {branch}")
            rich.print(f"Cloning...")
        bundle_url = await clone(
            ci_env,
            repo=repo,
            branch=branch,
            github_token=user_config.github_token,
            verbose=verbose,
        )
        if verbose:
            rich.print(f"[green]Cloned.")
            rich.print(bundle_url)

    if "build" in actions:
        if verbose:
            rich.print(f"Building...")

        env_variables = {}

        for env_var in build_env:
            key, value = env_var.split("=")
            env_variables[key] = value

        bundle_url = await build(
            ci_env=ci_env,
            bundle_url=bundle_url,
            type=type,
            env_variables=env_variables,
            verbose=verbose,
            architecture=arch,
        )
        if verbose:
            rich.print(f"[green]Built.")
            rich.print(bundle_url)

    if "deploy" in actions:
        if verbose:
            if product:
                rich.print(f"Deploying bundle from marketplace for product: {product}")
            rich.print(f"Deploying to env: {target}")
            rich.print(f"Deploying...")

        to_env = env_manager.get_staircase_env(target)
        if not to_env:
            raise click.ClickException("You have no such api in your envs saved.")
        env_token = await staircase.get_env_token(to_env)

        await deploy(
            ci_env=ci_env, url=bundle_url, env_token=env_token, verbose=verbose
        )
        if verbose:
            rich.print(f"[green]Deployed.")
