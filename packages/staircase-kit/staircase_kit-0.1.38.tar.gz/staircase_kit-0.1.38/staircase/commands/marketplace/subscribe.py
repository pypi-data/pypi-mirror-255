import rich
import click

from staircase.lib.postman_http_client import PostmanClient
from staircase.lib.click import async_cmd
from staircase.command_providers import (
    env_storage_provider,
    postman_provider,
)
from staircase.env_storage import EnvironmentStorage
from staircase.postman import Postman


@click.command(name="envs")
@click.option("-s", "--sync", flag_value=True)
@postman_provider()
@env_storage_provider()
@async_cmd
async def command(
    postman: Postman,
    env_storage: EnvironmentStorage,
    postman_client: PostmanClient,
    sync: bool,
    **_,
):
    """
    Import Staircase env to your Postman and use it with api product you imported.
    Creates StaircaseAPI workspace.  

    This command imports all envs that you have in `sc envs` group.

    If `-s` `--sync` flag is enabled. Envs that are in your Postman are same as `sc envs list` output.
    """
    workspaceid = postman.get_or_create_workspace()
    postman_envs = postman_client.request("environments").json()["environments"]
    envs = env_storage.get_all_envs()

    if sync:
        env_domain_names = [env.domain_name for env in envs]
        env_domain_names_to_postman_env_name = [
            get_postman_env_name_from_domain(edn) for edn in env_domain_names
        ]
        postman_envs_to_delete = filter(
            lambda p_env: p_env["name"] not in env_domain_names_to_postman_env_name,
            postman_envs,
        )
        for p_env in postman_envs_to_delete:
            postman.delete_env_by_id(p_env["id"])
            rich.print(f"[red] Delete env {p_env['name']}")


    for env in envs:
        postman_env_name = get_postman_env_name_from_domain(env.domain_name)

        envs_with_same_name = filter(
            lambda p_env: p_env["name"] == postman_env_name, postman_envs
        )
        [postman.delete_env_by_id(p_env["id"]) for p_env in envs_with_same_name]

        # create env

        postman_client.request(
            f"environments/?workspace={workspaceid}",
            "POST",
            json={
                "environment": {
                    "name": postman_env_name,
                    "values": [
                        {"key": "envUrl", "value": f"https://{env.domain_name}"},
                        {
                            "key": "apiKey",
                            "value": env.api_key,
                        },
                    ],
                }
            },
        )
        rich.print(f"[green]Imported {env.domain_name}")


def get_postman_env_name_from_domain(domain: str):
    return domain.split(".staircaseapi.com")[0]
