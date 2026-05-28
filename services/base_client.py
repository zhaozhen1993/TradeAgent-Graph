import httpx
import os


class BaseAPIClient:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    async def get(self, path: str, params: dict = None):
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{self.base_url}{path}", params=params, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def post(self, path: str, data: dict):
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(f"{self.base_url}{path}", json=data, headers=self.headers)
            resp.raise_for_status()
            return resp.json()