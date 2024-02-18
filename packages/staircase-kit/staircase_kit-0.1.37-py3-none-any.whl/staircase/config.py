import rich
import os
import json
from pydantic import BaseModel
from pathlib import Path
from typing import Optional


STAIRCASE_FOLDER = Path.home() / '.staircase'
DATA_FOLDER =  STAIRCASE_FOLDER / "data"
VAR_FOLDER = STAIRCASE_FOLDER / "var"
CONFIG_FILE_PATH = DATA_FOLDER / "config.json"
ENV_FILE_PATH = DATA_FOLDER / "staircase_envs.json"

class UserConfig(BaseModel):
    postman_api_key: Optional[str]
    marketplace_api_key: Optional[str]
    github_token: Optional[str]
    asana_token: Optional[str]


def get_user_cfg() -> UserConfig:
    if not os.path.exists(CONFIG_FILE_PATH):
        return UserConfig(
            postman_api_key=None,
            marketplace_api_key=None,
            github_token=None,
            asana_token=None
        )
    
    with open(CONFIG_FILE_PATH, "r") as f:
        try:
            config_file = json.load(f)
            user_config = UserConfig.parse_obj(config_file)
            return user_config
        except json.JSONDecodeError:
            rich.print("[red]Config is not valid, taking default values.")
            return UserConfig(
                postman_api_key=None,
                marketplace_api_key=None,
                github_token=None,
                asana_token=None
            )


def write_user_cfg(user_cfg: UserConfig):
    with open(CONFIG_FILE_PATH, "w+") as f:
        json.dump(user_cfg.dict(), f)
