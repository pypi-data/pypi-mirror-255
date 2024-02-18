import asyncio

from ..staircase_env import StaircaseEnvironment


async def clone(
    ci_env: StaircaseEnvironment, *, repo: str, branch: str, github_token: str, verbose: bool = False
):
    data = {
        "repository_name": repo,
        "github_token": github_token,
        "branch": branch,
        "github_account": "staircaseapi",
    }
    r = await ci_env.http_client.async_request(
        "code/clone",
        "POST",
        data=data,
    )
    r = await r.json()

    clone_id = r["bundle_id"]
    if verbose:
        print(f"Clone id: {clone_id}")

    while True:
        response = await ci_env.http_client.async_request(f"code/clone/{clone_id}")
        response_body = await response.json()
        status = response_body.get("clone_status")
        if status in ("IN_PROGRESS", "RUNNING"):
            await asyncio.sleep(10)
        elif status == "FAILED":
            if logs := response_body.get("logs"):
                logs = "".join(logs) if isinstance(logs, list) else logs
            raise Exception()
        elif status == "SUCCEEDED":
            url: str = response_body["source_url"]
            return url
        else:
            raise Exception()
