import logging
import re
from typing import Optional, Union, Generator

import httpx
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ipfabric.tools import VALID_REFS

logger = logging.getLogger("ipfabric")


class AccessToken(httpx.Auth):
    def __init__(self, client: httpx.Client):
        self.client = client

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        response = yield request

        if response.status_code == 401:
            response.read()
            if "API_EXPIRED_ACCESS_TOKEN" in response.text:
                resp = self.client.post("/api/auth/token")  # Use refreshToken in Cookies to get new accessToken
                resp.raise_for_status()  # Response updates accessToken in shared CookieJar
                request.headers["Cookie"] = "accessToken=" + self.client.cookies["accessToken"]  # Update request
                yield request
        return response


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="ipf_", extra="allow")
    url: Optional[str] = None
    version: Optional[Union[int, float, str]] = None
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    snapshot: Optional[str] = None
    verify: Union[bool, int, str] = True
    timeout: Optional[float] = None

    @field_validator("version")
    @classmethod
    def _valid_version(cls, v: Union[None, int, float, str]) -> Union[None, str]:
        if v and isinstance(v, (int, float)):
            v = "v" + str(v)
        if not v or re.match(r"v\d(\.\d)?", v):
            return v
        else:
            raise ValueError(f"IPF_VERSION ({v}) is not valid, must be like `v#` or `v#.#`.")

    @field_validator("snapshot")
    @classmethod
    def _valid_snapshot(cls, v: Union[None, str]) -> Union[None, str]:
        if v is None or v in VALID_REFS:
            return v
        elif re.match(r"^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$", v.lower()):
            return v.lower()
        else:
            raise ValueError(f"IPF_SNAPSHOT ({v}) is not valid, must be a UUID or one of {VALID_REFS}.")

    @field_validator("verify")
    @classmethod
    def _verify(cls, v: Union[bool, int, str]) -> Union[bool, str]:
        if isinstance(v, bool):
            return v
        if v.lower() in {0, "0", "off", "f", "false", "n", "no", 1, "1", "on", "t", "true", "y", "yes"}:
            return False if v.lower() in {0, "0", "off", "f", "false", "n", "no"} else True
        else:
            return v

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Needed for context"""
        pass
