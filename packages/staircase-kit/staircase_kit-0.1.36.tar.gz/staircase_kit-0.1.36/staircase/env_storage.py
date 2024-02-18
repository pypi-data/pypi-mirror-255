import os
import json
from typing import List, Optional
from pydantic import BaseModel, parse_obj_as
from pydantic.json import pydantic_encoder


from .config import ENV_FILE_PATH 


class Env(BaseModel):
    domain_name: str
    api_key: str


class EnvironmentStorage:
    envs: Optional[List[Env]]

    def __init__(self):
        self._create_default_config_file()

    def _create_default_config_file(self):
        if not os.path.exists(ENV_FILE_PATH):
            with open(ENV_FILE_PATH,"w+") as f:
                json.dump([], f)

    def _read_file(self):
        with open(ENV_FILE_PATH, "r") as f:
            envs = json.load(f)
            self.envs = parse_obj_as(List[Env], envs)

    def get_all_envs(self):
        self._read_file()
        return self.envs

    def add_env(self, env: Env):
        with open(ENV_FILE_PATH, "r+") as f:
            envs = json.load(f)

        envs = parse_obj_as(List[Env], envs)
        env_domains = map(lambda e: e.domain_name, envs)

        with open(ENV_FILE_PATH, "w+") as f:
            if env.domain_name in env_domains:
                raise EnvAlreadyExists()
            envs.append(env)
            f.write(json.dumps(envs, default=pydantic_encoder, indent=2))

    def remove_env(self, index: int):
        with open(ENV_FILE_PATH, "r+") as f:
            envs = json.load(f)
        envs: List[Env] = parse_obj_as(List[Env], envs)

        with open(ENV_FILE_PATH, "w+") as f:
            envs.pop(index)
            f.write(json.dumps(envs, default=pydantic_encoder, indent=2))


class EnvAlreadyExists(Exception):
    ...