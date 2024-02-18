from staircase.postman import StaircaseNotFoundBundle
from staircase.lib.sdk import StaircaseEnvironment

from .config import UserConfig


class Staircase:
    def __init__(self, config: UserConfig):
        if not config.marketplace_api_key:
            raise Exception("No marketplace_api_key found in config")
        self.market_place_env = StaircaseEnvironment(
            domain="marketplace.staircaseapi.com", api_key=config.marketplace_api_key
        )

    async def get_marketplace_onltology_representation(self):
        return await self.market_place_env.http_client.async_request(
            "marketplace/ontology/representation/raw"
        )

    async def toggle_health_check_for_product(
        self, env: StaircaseEnvironment, product_id: str, is_disabled: bool
    ):
        return await env.http_client.async_request(
            "code-health-checker/development-products",
            method="POST",
            data={"product_id": product_id, "is_disabled": is_disabled},
        )

    async def create_transaction(self, staircase_env, label):
        return await staircase_env.http_client.async_request(
            "persistence/transactions", "POST", data={"label": label}
        )

    async def get_latest_transaction_by_label(self, staircase_env, label):
        response = await staircase_env.http_client.async_request(
            f"persistence/transactions?filter=label+eq+{label}", "GET"
        )
        json_ = await response.json()
        transactions = json_["transactions"]
        if len(transactions) > 0:
            return transactions[0]["transaction_id"]
        return None

    async def create_collection(self, staircase_env, transaction_id, collection):
        return await staircase_env.http_client.async_request(
            f"persistence/transactions/{transaction_id}/collections",
            "POST",
            data={"data": collection, "metadata": {"version": 3, "validation": True}},
        )

    async def get_all_product_components(self):
        url = f"marketplace/ontology/representation/raw"
        response = await self.market_place_env.http_client.async_request(url)
        response_json = await response.json()
        products = response_json.get("products", [])

        return products

    async def get_all_representation(self):
        url = f"marketplace/ontology/representation/raw"
        response = await self.market_place_env.http_client.async_request(url)
        response_json = await response.json()
        return response_json

    async def retrieve_product_component(self, product_component_name):
        url = f"marketplace/products/{product_component_name}"
        response = await self.market_place_env.http_client.async_request(url)

        return await response.json()

    async def get_env_token(self, staircase_env):
        response = await staircase_env.http_client.async_request(
            f"environment-manager/environment"
        )
        env_data = await response.json()
        token = env_data["staircase_environment"]["environment_token"]
        return token

    async def get_latest_bundle(self, component_name, is_data=False) -> str:
        next_token = None

        
        while True:
            url = f"marketplace/{'data' if is_data else 'products'}/{component_name}/bundles"
            if next_token:
                url += f"?next_token={next_token}"

            res = await self.market_place_env.http_client.async_request(url)
            if res.status == 404:
                raise StaircaseNotFoundBundle("Recieve 404")

            if res.status == 403:
                raise StaircaseNotFoundBundle("Component name might contain slash")

            response_json = await res.json()
            bundles = response_json["bundles"]
            page = response_json["page"]

            for bundle in bundles:
                if not bundle["bundle_status"] == "Valid" or "bundle_url" not in bundle:
                    continue
                return bundle["bundle_url"]

            next_token = page.get("next_token")
            if not next_token:
                break

        raise StaircaseNotFoundBundle("Not found latest bundle with success assess")
