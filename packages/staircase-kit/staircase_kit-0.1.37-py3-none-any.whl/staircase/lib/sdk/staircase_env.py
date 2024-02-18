from typing import Optional
import json
from dataclasses import dataclass

from .staircase_http_client import StaircaseHttpClient


@dataclass
class StaircaseEnvironment:
    domain: str
    api_key: str

    http_client: Optional[StaircaseHttpClient] = None

    def __post_init__(self):
        self.http_client = StaircaseHttpClient(env=self)
