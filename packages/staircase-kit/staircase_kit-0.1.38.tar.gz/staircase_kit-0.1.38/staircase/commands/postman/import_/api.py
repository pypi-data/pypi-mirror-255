# TODO add note that this command removes collections with same names
# TODO add imported collection not as swagger but as component name
import zipfile
import os
import rich
import shutil
import yaml
import requests
import click
from typing import Union
from staircase.config import VAR_FOLDER

from staircase.lib.shutil import onerror
from staircase.lib.fzf import prompt
from staircase.lib.postman_http_client import PostmanClient
from staircase.lib.click import async_cmd

from staircase.command_providers import (
    staircase_provider,
    postman_provider,
)
from staircase.postman import Postman
from staircase.staircase import Staircase, StaircaseNotFoundBundle


@click.command(name="api")
@click.option("-c", "--component")
@click.option("-a", "--all", flag_value=True, default=False)
@click.option("-d", "--data", flag_value=True, default=False)
@staircase_provider()
@postman_provider()
@async_cmd
async def command(
    all: bool,
    data: bool,
    component: Union[str, bool],
    staircase: Staircase,
    postman: Postman,
    postman_client: PostmanClient,
):
    """
    Import Staircase product to your Postman and use it with environment you imported.
    Creates StaircaseAPI workspace.

    """

    components = (await staircase.get_all_representation())["components"]
    if not components:
        raise Exception("No components found")
    components_names = map(lambda e: e["component_name"], components)

    if not all and not component:
        components_names = prompt(
            components_names,
            header="Select your component name | Select multiple via TAB",
            multi=True,
        )

    workspaceid = postman.get_or_create_workspace()

    for component_name in components_names:
        click.echo(f"Importing component {component_name}...")
        os.chdir(VAR_FOLDER)

        try:
            bundle_url = await staircase.get_latest_bundle(component_name, data)
        except StaircaseNotFoundBundle:
            rich.print(
                f"[red]Not found latest for component {component_name} in marketplace"
            )
            continue

        click.echo(f"Downloading bundle...")
        click.echo(bundle_url)
        r = requests.get(bundle_url, allow_redirects=True)
        click.echo(f"Downloaded")
        with open(VAR_FOLDER / "bundle.zip", "wb") as f:
            f.write(r.content)

        bundle_folder_path = VAR_FOLDER / "bundle"

        with zipfile.ZipFile(VAR_FOLDER / "bundle.zip", "r") as zip_ref:
            zip_ref.extractall(bundle_folder_path)

        swagger_file_path = bundle_folder_path / "docs" / "swagger.yml"

        if not os.path.exists(swagger_file_path):
            click.echo("Not found swagger file in component repo, nothing to import.")
            continue

        with open(swagger_file_path, "r", encoding="utf-8") as f:
            swagger_json = yaml.safe_load(f)
            swagger_json["info"]["title"] = component_name

        postman.cleanup_postman_collections(component_name, workspaceid)
        shutil.rmtree(bundle_folder_path, onerror=onerror)

        response = postman_client.request(
            f"import/openapi?workspace={workspaceid}",
            method="POST",
            json={"type": "json", "input": swagger_json},
        )

        response = response.json()
        collection_id = response["collections"][0]["id"]
        if len(response["collections"]) > 1:
            raise Exception("You can not have more than 1 collection imported. File CR")

        response = postman_client.request(
            f"collections/{collection_id}?workspace={workspaceid}"
        )
        collection_create_body = response.json()
        base_url = collection_create_body["collection"]["variable"][0]["value"]
        prefix_len = len("https://documentation.staircaseapi.com/")
        base_path = base_url[prefix_len:]

        collection_create_body["collection"]["variable"][0]["value"] = (
            "{{envUrl}}/" + base_path
        )
        # del collection_create_body["collection"]["variable"][0]["type"]

        postman_client.request(
            f"collections/{collection_id}?workspace={workspaceid}", method="DELETE"
        )
        postman_client.request(
            f"collections?workspace={workspaceid}",
            method="POST",
            json=collection_create_body,
        )
        rich.print(f"[green]{component_name} imported successfully")
