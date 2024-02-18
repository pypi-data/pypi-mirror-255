import abc
import os
from typing import Any, Awaitable, Dict, Union

import jwt

from original_sdk.types.original_response import OriginalResponse

DEFAULT_BASE_URL = "https://api.getoriginal.com"
DEFAULT_API_VERSION = "v1"


class BaseOriginalClient(abc.ABC):
    def __init__(
        self, api_key: str, api_secret: str, timeout: float = 6.0, **options: Any
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout

        if os.getenv("ORIGINAL_TIMEOUT"):
            self.timeout = float(os.environ["ORIGINAL_TIMEOUT"])

        self.options = options
        self.base_url = DEFAULT_BASE_URL
        self.api_version = DEFAULT_API_VERSION

        if options.get("base_url"):
            self.base_url = options["base_url"]
        elif os.getenv("ORIGINAL_URL"):
            self.base_url = os.environ["ORIGINAL_URL"]

        if options.get("api_version"):
            self.api_version = options["api_version"]
        elif os.getenv("API_VERSION"):
            self.api_version = os.environ["API_VERSION"]

        self.base_url = self.base_url.rstrip("/")

        self.token = jwt.encode(
            {"resource": "*", "action": "*", "user_id": "*", "api_key": api_key},
            api_secret,
        )

    def get_default_params(self) -> Dict[str, str]:
        return {"api_key": self.api_key, "api_secret": self.api_secret}

    def create_token(self) -> str:
        return jwt.encode(
            {"resource": "*", "action": "*", "user_id": "*", "api_key": self.api_key},
            self.api_secret,
        )

    def create_search_params(
        self,
        filter_conditions: Dict,
        query: Union[str, Dict],
        **options: Any,
    ) -> Dict[str, Any]:
        params = options.copy()
        if isinstance(query, str):
            params.update({"query": query})
        else:
            params.update({"message_filter_conditions": query})

        params.update({"filter_conditions": filter_conditions})

        return params

    @abc.abstractmethod
    def create_user(
        self, email: str, client_id: str
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Create an Original user.
        """
        pass

    @abc.abstractmethod
    def get_user(
        self, uid: str
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Get an Original user.

        :param uid: the user uid
        :return:
        """
        pass

    @abc.abstractmethod
    def get_user_by_email(
        self, email: str
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Gets a user by email

        :param email: the users email
        :return:
        """
        pass

    @abc.abstractmethod
    def get_user_by_client_id(
        self, client_id: str
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Gets a user by client_id

        :param client_id: the users email
        :return:
        """
        pass

    @abc.abstractmethod
    def get_collection(
        self, uid: str
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Get an Original collection.

        :param uid: the collection uid
        :return:
        """
        pass

    @abc.abstractmethod
    def create_asset(
        self, **asset_data: Any
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Create an Original asset.

        :param asset_data: the asset data
        :return:
        """
        pass

    @abc.abstractmethod
    def edit_asset(
        self, asset_uid: str, **asset_data: Any
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Update an Original asset.

        :param asset_uid: the asset uid
        :param asset_data: the asset data
        :return:
        """
        pass

    @abc.abstractmethod
    def get_asset(
        self, asset_uid: str
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Get an Original asset.

        :param asset_uid: the asset uid
        :return:
        """
        pass

    @abc.abstractmethod
    def get_assets_by_user_uid(
        self, app_user_uid: str
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Get an Original asset by owner uid.

        :param app_user_uid: the app user uid
        :return:
        """
        pass

    @abc.abstractmethod
    def create_transfer(
        self, **transfer_data: Any
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Create an Original transfer.

        :param transfer_data: the transfer data
        :return:
        """
        pass

    @abc.abstractmethod
    def get_transfer(
        self, transfer_uid: str
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Get an Original transfer.

        :param transfer_uid: the transfer uid
        :return:
        """
        pass

    @abc.abstractmethod
    def get_transfers_by_user_uid(
        self, app_user_uid: str
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Get an Original transfer by user uid.

        :param app_user_uid: the app user uid
        :return:
        """
        pass

    @abc.abstractmethod
    def create_burn(
        self, **burn_data: Any
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Create an Original burn.

        :param burn_data: the burn data
        :return:
        """
        pass

    @abc.abstractmethod
    def get_burn(
        self, burn_uid: str
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Get an Original burn.

        :param burn_uid: the burn uid
        :return:
        """
        pass

    @abc.abstractmethod
    def get_burns_by_user_uid(
        self, app_user_uid: str
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Get an Original burn by user uid.

        :param app_user_uid: the app user uid
        :return:
        """
        pass

    @abc.abstractmethod
    def get_deposit(
        self, user_uid: str
    ) -> Union[OriginalResponse, Awaitable[OriginalResponse]]:
        """
        Get an Original deposit by user uid.

        :param app_user_uid: the app user uid
        :return:
        """
        pass
