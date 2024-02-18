import rich
import click
from itertools import product
from ulid import ULID

from staircase.lib.fzf import prompt
from staircase.staircase_asana import StaircaseAsana, SEARCHES_BY_TEAM
from staircase.lib.click import async_cmd
from staircase.command_providers import user_config_provider, env_manager_provider
from staircase.config import UserConfig
import webbrowser
from staircase.command_providers import env_storage_provider, staircase_provider, EnvironmentManager
from staircase.lib.sdk.staircase_env import StaircaseEnvironment
from staircase.env_storage import EnvironmentStorage
from staircase.staircase import Staircase


@click.command(name="searches")
@click.option("--open-browser", "-o", help="Open in browser", is_flag=True)
@click.option("--save", "-s", help="Saves in persistence.", is_flag=True)
@click.option("--env", "-e", help="Target env to save")
@user_config_provider()
@env_storage_provider()
@staircase_provider()
@env_manager_provider()
@async_cmd
async def command(
    open_browser: bool,
    save: bool,
    env: str,
    user_config: UserConfig,
    env_storage: EnvironmentStorage,
    staircase: Staircase,
    env_manager: EnvironmentManager
):
    if not user_config.asana_token:
        raise Exception("No asana token in config")
    asana = StaircaseAsana(token=user_config.asana_token)

    teams = asana.get_staircase_teams()

    verbose_names = []
    searches_combinations = product(SEARCHES_BY_TEAM, teams)
    # Genearting constructed searches
    searches = map(
        lambda search_combination: search_combination[0](
            team=search_combination[1], staircase_asana=asana
        ),
        searches_combinations,
    )


    if save:
        env: Optional[StaircaseEnvironment] = env_manager.get_staircase_env(env)
        await save_searches_in_persistence(searches, env, staircase)
        
        return

    enumed_searches = list(enumerate(searches))
    for idx, search in enumed_searches:
        verbose_names.append(f"{idx}: {search.verbose_name}")

    selected = prompt(verbose_names)[0]
    idx = int(selected.split(":")[0])
    search = enumed_searches[idx][1]

    if open_browser:
        webbrowser.open(search.search_url, new=0, autoraise=True)
    else:
        rich.print(search.search_url)


async def save_searches_in_persistence(searches, env, staircase: Staircase):

    transaction_id = await staircase.get_latest_transaction_by_label(env, "asana-searches")
    if not transaction_id:
        response = await staircase.create_transaction(env, "asana-searches")
        js_ = await response.json()
        transaction_id = js_["transaction_id"]

    saved_searches = []
    for search in searches:
        try:
            saved_searches.append({
                "search_url": search.search_url,
                "search_terms": search.verbose_name,
                "@id": str(ULID()),
                "@type": "saved_search",
            })
        except Exception as e:
            print(search.verbose_name)


    collection_to_save = {"saved_searches": saved_searches}

    response = await staircase.create_collection(
        env, transaction_id, collection_to_save
    )
    print(response)
