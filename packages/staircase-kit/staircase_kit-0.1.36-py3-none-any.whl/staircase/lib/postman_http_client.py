import requests
from dataclasses import dataclass

@dataclass
class PostmanClient:
    api_key: str

    def request(self, url, method="GET", data=None, json=None):
        url = f"https://api.getpostman.com/{url}"

        headers = {
        'Content-Type': 'application/json',
        'X-API-Key': self.api_key
        }

        response = requests.request(method, url, headers=headers, json=json, data = data)
        return response