import json
from typing import Optional 
from staircase.lib.fzf import prompt
from .staircase import Staircase

async def select_product_git_repo(staircase: Staircase, prompt_header: str) -> Optional[str]:
    products = await staircase.get_all_product_components()

    product_names = list(map(lambda e: e["product_name"], products))
    product_names_selected = prompt(product_names, header=prompt_header)
    if not product_names_selected:
        return None
    product_name_selected = product_names_selected[0]
    
    product_data = await staircase.retrieve_product_component(product_name_selected)
    repo_url = product_data.get("bundle_meta")['service-code']['repository_url']
    repo_url = repo_url.split("StaircaseAPI/")[1]

    return repo_url




def select_env_domain():
    with open("data/staircase_envs.json") as fp_envs:
        envs = json.load(fp_envs)
        env_domains = list(map(lambda e: e["domain_name"], envs))
        selected = prompt(env_domains)
        if not selected:
            return None
        return selected[0]
