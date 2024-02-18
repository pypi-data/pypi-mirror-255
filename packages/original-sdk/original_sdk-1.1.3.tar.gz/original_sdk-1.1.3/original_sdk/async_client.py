import json
from types import TracebackType
from typing import Any, AsyncContextManager, Callable, Dict, Optional, Type

import aiohttp

from .__pkg__ import __version__
from .base.client import BaseOriginalClient
from .base.exceptions import OriginalAPIException
from .types.original_response import OriginalResponse


def get_user_agent() -> str:
    return f"original_sdk-python-client-aio-{__version__}"


def get_default_header() -> Dict[str, str]:
    base_headers = {
        "Content-type": "application/json",
        "X-ORIGINAL-Client": get_user_agent(),
    }
    return base_headers


class OriginalAsyncClient(BaseOriginalClient, AsyncContextManager):
    def __init__(
        self, api_key: str, api_secret: str, timeout: float = 6.0, **options: Any
    ):
        super().__init__(
            api_key=api_key, api_secret=api_secret, timeout=timeout, **options
        )
        self.session = aiohttp.ClientSession(
            base_url=self.base_url,
            connector=aiohttp.TCPConnector(keepalive_timeout=59.0),
        )

    def set_http_session(self, session: aiohttp.ClientSession) -> None:
        """
        You can use your own `aiohttp.ClientSession` instance. This instance
        will be used for underlying HTTP requests.
        Make sure you set up a `base_url` for the session.
        """
        self.session = session

    async def _parse_response(
        self, response: aiohttp.ClientResponse
    ) -> OriginalResponse:
        text = await response.text()
        try:
            parsed_result = await response.json() if text else {}
        except aiohttp.ClientResponseError:
            raise OriginalAPIException(text, response.status)
        if response.status >= 399:
            raise OriginalAPIException(text, response.status)

        return OriginalResponse(parsed_result, dict(response.headers), response.status)

    async def _make_request(
        self,
        method: Callable,
        relative_url: str,
        params: Dict = None,
        data: Any = None,
    ) -> OriginalResponse:
        params = params or {}
        params = {
            k: str(v).lower() if isinstance(v, bool) else v for k, v in params.items()
        }
        data = data or {}
        serialized = None
        default_params = self.get_default_params()
        default_params.update(params)
        headers = get_default_header()
        headers["Authorization"] = f"Bearer {self.token}"
        headers["X-API-KEY"] = self.api_key

        if method.__name__ in ["post", "put", "patch"]:
            serialized = json.dumps(data)
        async with method(
            f"/api/{self.api_version}/" + relative_url.lstrip("/"),
            data=serialized,
            headers=headers,
            params=default_params,
            timeout=self.timeout,
        ) as response:
            return await self._parse_response(response)

    async def put(
        self, relative_url: str, params: Dict = None, data: Any = None
    ) -> OriginalResponse:
        return await self._make_request(self.session.put, relative_url, params, data)

    async def post(
        self, relative_url: str, params: Dict = None, data: Any = None
    ) -> OriginalResponse:
        return await self._make_request(self.session.post, relative_url, params, data)

    async def get(self, relative_url: str, params: Dict = None) -> OriginalResponse:
        return await self._make_request(self.session.get, relative_url, params, None)

    async def delete(self, relative_url: str, params: Dict = None) -> OriginalResponse:
        return await self._make_request(self.session.delete, relative_url, params, None)

    async def patch(
        self, relative_url: str, params: Dict = None, data: Any = None
    ) -> OriginalResponse:
        return await self._make_request(self.session.patch, relative_url, params, data)

    async def create_user(self, email: str, client_id: str) -> OriginalResponse:
        return await self.post("user", data={"email": email, "client_id": client_id})

    async def get_user(self, user_id: str) -> OriginalResponse:
        return await self.get(f"user/{user_id}")

    async def get_user_by_email(self, email: str) -> OriginalResponse:
        return await self.get("user", params={"email": email})

    async def get_user_by_client_id(self, client_id: str) -> OriginalResponse:
        return await self.get("user", params={"client_id": client_id})

    async def get_collection(self, uid: str) -> OriginalResponse:
        return await self.get(f"collection/{uid}")

    async def create_asset(self, **asset_data: Any) -> OriginalResponse:
        return await self.post("asset", data=asset_data)

    async def edit_asset(self, asset_uid: str, **asset_data: Any) -> OriginalResponse:
        return await self.put(f"asset/{asset_uid}", data=asset_data)

    async def get_asset(self, asset_uid: str) -> OriginalResponse:
        return await self.get(f"asset/{asset_uid}")

    async def get_assets_by_user_uid(self, app_user_uid: str) -> OriginalResponse:
        return await self.get("asset", params={"user_uid": app_user_uid})

    async def create_transfer(self, **transfer_data: Any) -> OriginalResponse:
        return await self.post("transfer", data=transfer_data)

    async def get_transfer(self, transfer_uid: str) -> OriginalResponse:
        return await self.get(f"transfer/{transfer_uid}")

    async def get_transfers_by_user_uid(self, app_user_uid: str) -> OriginalResponse:
        return await self.get("transfer", params={"user_uid": app_user_uid})

    async def create_burn(self, **burn_data: Any) -> OriginalResponse:
        return await self.post("burn", data=burn_data)

    async def get_burn(self, burn_uid: str) -> OriginalResponse:
        return await self.get(f"burn/{burn_uid}")

    async def get_burns_by_user_uid(self, app_user_uid: str) -> OriginalResponse:
        return await self.get("burn", params={"user_uid": app_user_uid})

    async def get_deposit(self, user_uid: str) -> OriginalResponse:
        return await self.get("deposit", params={"user_uid": user_uid})

    async def close(self) -> None:
        await self.session.close()

    async def __aenter__(self) -> "OriginalAsyncClient":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()
