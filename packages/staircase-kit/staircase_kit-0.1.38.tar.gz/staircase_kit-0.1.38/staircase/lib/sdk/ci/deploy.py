import time

from ..staircase_env import StaircaseEnvironment

def deploy_data(url, to_env, ci_env):
    check_deploy = ci_env.deployer_product.check_deploy_data
    r = ci_env.deployer_product.deploy_data(url, to_env)
    id_ = r["bundle_id"]

    while True:
        response_body = check_deploy(id_)
        status = response_body.get("deploy_status")

        if status in ("IN_PROGRESS", "RUNNING"):
            time.sleep(10)
        elif status == "FAILED":
            if logs := response_body.get("logs"):
                logs = "".join(logs) if isinstance(logs, list) else logs
            print("Error deploy")
            raise Exception(response_body)
        else:
            return


async def deploy(url, ci_env: StaircaseEnvironment, env_token: str, verbose: bool = False):

    data = {
        "artifacts_url": url,
        "environment_token": env_token
    }
    r = await ci_env.http_client.async_request( "infra-deployer/deployments", "POST", data)
    r = await r.json()
    id_ = r["bundle_id"]
    if verbose:
        print(f"Deploy id: {id_}")


    while True:
        r = await ci_env.http_client.async_request( f"infra-deployer/deployments/{id_}")
        response_body = await r.json()
        status = response_body.get("deploy_status")

        if status in ("IN_PROGRESS", "RUNNING"):
            time.sleep(10)
        elif status == "FAILED":
            if logs := response_body.get("logs"):
                logs = "".join(logs) if isinstance(logs, list) else logs
            raise Exception(response_body)
        elif status == "SUCCEEDED":
            return
        else:
            raise Exception("Unknown status")
