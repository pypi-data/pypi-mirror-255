import dataclasses
import datetime
import logging
import os
from enum import unique, Enum, auto
from typing import Optional, Any

import requests


@unique
class TqSystemEnums(Enum):
    CRM = auto()
    GIS = auto()
    IND_V1 = auto()
    IND_V2 = auto()


class TqDefaultConfig:
    @staticmethod
    def get_var(
        suffix: str,
        tq_sys_enum: Optional[TqSystemEnums] = None,
        raise_error: bool = True,
    ) -> str:
        if tq_sys_enum:
            key = f"TQBUS_{tq_sys_enum.name}_{suffix}"
        else:
            key = f"TQBUS_{suffix}"
        var = os.getenv(key)
        if raise_error and not var:
            raise ValueError(f"{key} env var not set!")
        return var

    @staticmethod
    def date_encoder(dt: Optional[datetime.date]) -> Optional[str]:
        default_date_format = "%Y-%m-%d"
        if not dt:
            return dt
        DATEFORMAT = (
            TqDefaultConfig.get_var("DATEFORMAT", None, False) or default_date_format
        )
        return dt.strftime(DATEFORMAT)

    @staticmethod
    def datetime_encoder(dt: Optional[datetime.datetime]) -> Optional[str]:
        default_datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        if not dt:
            return dt
        DATETIMEFORMAT = (
            TqDefaultConfig.get_var("DATETIMEFORMAT", None, False)
            or default_datetime_format
        )
        return dt.strftime(DATETIMEFORMAT)

    @staticmethod
    def date_decoder(date_string: Optional[str]) -> Optional[datetime.date]:
        default_date_format = "%Y-%m-%d"
        if not date_string:
            return date_string
        DATEFORMAT = (
            TqDefaultConfig.get_var("DATEFORMAT", None, False) or default_date_format
        )
        return datetime.datetime.strptime(date_string, DATEFORMAT)

    @staticmethod
    def datetime_decoder(date_string: Optional[str]) -> Optional[datetime.datetime]:
        default_datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        if not date_string:
            return date_string
        DATETIMEFORMAT = (
            TqDefaultConfig.get_var("DATETIMEFORMAT", None, False)
            or default_datetime_format
        )
        return datetime.datetime.strptime(date_string, DATETIMEFORMAT)


@dataclasses.dataclass
class TokenManager:
    auth_url: str
    username: str
    password: str
    __token: str = dataclasses.field(default=None)
    __expires_at: datetime.datetime = dataclasses.field(
        default_factory=datetime.datetime.utcnow
    )

    def generate_token(self) -> None:
        url = self.auth_url
        if not url:
            self.__token = "NO_AUTH_URL"
            self.__expires_at = self.__expires_at + datetime.timedelta(seconds=1000 * 3)
            return
        headers = {"Content-Type": "application/json"}
        payload = {"username": self.username, "password": self.password}
        response = requests.post(url=url, headers=headers, json=payload)
        response.raise_for_status()
        body = response.json()
        if not body.get("success"):
            raise requests.exceptions.RequestException(body)
        self.__token = body["token"]
        expires_in: int = body["expires_in"]
        # using last generated instead of utcnow() to allow room for error
        self.__expires_at = self.__expires_at + datetime.timedelta(seconds=expires_in / 1000)

    def token(self):
        if not self.__token or datetime.datetime.utcnow() >= self.__expires_at:
            self.generate_token()
        return self.__token


@dataclasses.dataclass
class TqSystem:
    tq_system_enum: TqSystemEnums
    token_manager: Optional[TokenManager] = dataclasses.field(default=None)

    def __post_init__(self):
        # create token manager if not created
        if not self.token_manager:
            self.token_manager = TokenManager(
                auth_url=self.auth_url, username=self.username, password=self.password
            )

    def _get_env_var(self, suffix: str) -> str:
        return TqDefaultConfig.get_var(suffix, self.tq_system_enum)

    @property
    def base_url(self) -> str:
        return self._get_env_var("BASEURL")

    @property
    def username(self) -> str:
        if not self.auth_url:
            return "NO_AUTH_URL"
        return self._get_env_var("USERNAME")

    @property
    def password(self) -> str:
        if not self.auth_url:
            return "NO_AUTH_URL"
        return self._get_env_var("PASSWORD")

    @property
    def auth_url(self) -> str:
        urls_dict: dict[TqSystemEnums, str] = {
            TqSystemEnums.CRM: f"{self.base_url}authenticate/login",
            TqSystemEnums.GIS: f"{self.base_url}oauth/token",
            TqSystemEnums.IND_V2: f"{self.base_url}authenticate/login",
        }
        return urls_dict.get(self.tq_system_enum)

    def get_default_headers(self, authenticated=True) -> dict:
        headers = {"Content-Type": "application/json"}
        if not authenticated:
            return headers
        token = self.token_manager.token()
        headers["Authorization"] = f"Bearer {token}"
        return headers

    def request(self, method: str, url: str, **kwargs) -> Any:
        headers = (
            kwargs.get("headers") or self.get_default_headers()
        )  # use passed if any or generate
        kwargs["headers"] = headers  # inject headers
        logging.debug(f"url={url}")
        response = requests.request(method=method, url=url, **kwargs)
        logging.debug(f"response: {response}")
        if response.status_code >= 300:  # inject content to reason
            response.reason = response.reason or response.content
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and not data.get("success", True):
            raise requests.exceptions.RequestException(data)
        logging.debug(f"data={data}")
        return data
