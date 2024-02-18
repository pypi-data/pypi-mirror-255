from dataclasses import dataclass
import aiohttp
import time

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .staircase_env import StaircaseEnvironment


def fix_retry(times=10):
    """Use to fight with random 403 error"""

    def decorator(func):
        async def newfn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                response = None
                try:
                    response = await func(*args, **kwargs)
                    if response.status != 403:
                        return response
                except aiohttp.ClientResponseError as e:
                    status = e.status
                    if status != 403:
                        raise e
                except aiohttp.ServerDisconnectedError as e:
                    ...

                attempt += 1
                time.sleep(1)

            response = await func(*args, **kwargs)
            return response

        return newfn

    return decorator


@dataclass
class StaircaseHttpClient:
    env: "StaircaseEnvironment"

    @fix_retry()
    async def async_request(
        self, url, method="GET", data=None, raise_for_status=True
    ) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession() as session:

            async with session.request(
                method,
                f"https://{self.env.domain}/{url}",
                json=data,
                headers={"x-api-key": self.env.api_key},
                raise_for_status=raise_for_status,
            ) as response:
                await response.text()
                return response
