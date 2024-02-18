import sys
from typing import Literal
import time

from ..staircase_env import StaircaseEnvironment


async def build(
    ci_env: StaircaseEnvironment,
    bundle_url,
    type: Literal["service", "data", "frontend"] = "service",
    env_variables: dict = None,
    verbose: bool = False,
    architecture: Literal["X86_64", "ARM64"] = "X86_64",
) -> str:
    if not env_variables:
        env_variables = {}

    if type == "service":
        url = "infra-builder/builds"
    elif type == "data":
        url = "infra-builder/data"
    elif type == "frontend":
        url = "infra-builder/frontend"
    elif type == "chat":
        url = "infra-builder/chat"

    try:
        data = {"source_url": bundle_url}
        if env_variables:
            data["env_variables"] = env_variables
        data["architecture"] = architecture
        r = await ci_env.http_client.async_request(url, "POST", data=data)
    except Exception as e:
        print(e.message)
        raise e
    r = await r.json()
    id_ = r["build_id"]
    if verbose:
        print(f"Build id: {id_}")

    while True:
        response = await ci_env.http_client.async_request(f"{url}/{id_}")
        response_body = await response.json()

        status = response_body.get("status")
        if status in ("IN_PROGRESS", "RUNNING"):
            time.sleep(15)
        elif status == "FAILED":
            if logs := response_body.get("logs"):
                logs = "".join(logs) if isinstance(logs, list) else logs
            raise BuildFailed(logs)
        else:
            url = response_body["artifacts_url"]
            return url


class BuildFailed(Exception):
    ...
