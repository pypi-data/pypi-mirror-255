import json
import logging
from collections import OrderedDict
from http.cookiejar import CookieJar
from importlib import metadata
from ipaddress import IPv4Address, AddressValueError
from typing import Optional, Union, Dict, List, Any
from urllib.parse import urljoin
from uuid import UUID
from warnings import warn

import dotenv
import httpx
from httpx import Client, URL

from ipfabric.auth import Settings, AccessToken
from ipfabric.models import Snapshot, SNAPSHOT_COLUMNS, OAS
from ipfabric.settings.user_mgmt import User
from ipfabric.tools import VALID_REFS

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

OAS_DIR = files("ipfabric.oas")

logger = logging.getLogger("ipfabric")

LAST_ID, PREV_ID, LASTLOCKED_ID = VALID_REFS


class IPFabricAPI(Client):
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_version: Optional[str] = None,
        snapshot_id: Optional[str] = None,
        auth: Optional[Any] = None,
        unloaded: bool = False,
        env_file: Optional[str] = None,
        streaming: bool = True,
        **kwargs,
    ):
        """Initializes the IP Fabric Client

        Args:
            base_url: IP Fabric instance provided in 'base_url' parameter, or the 'IPF_URL' environment variable
            api_version: [Optional] Version of IP Fabric API
            auth: API token, tuple (username, password), or custom Auth to pass to httpx
            snapshot_id: IP Fabric snapshot ID to use by default for database actions - defaults to '$last'
            unloaded: True to load metadata from unloaded snapshots
            env_file: Path to .env file to load
            **kwargs: Keyword args to pass to httpx
        """
        if {kwargs.get(i, None) for i in ["token", "username", "password"]} != {None}:  # TODO: Remove v7.0
            warn(
                "Use of `token='<TOKEN>'` or `username='<USER>', password='<PASS>'` authentication will be deprecated "
                "in v7.0.X, please use `auth='<TOKEN>'` or `auth=('<USER>','<PASS>')` instead.\n"
                "This does not apply to .env file or environment variables (IPF_TOKEN, IPF_USERNAME, IPF_PASSWORD).\n"
                "This is to support custom authentication methods that will be passed directly to HTTPX.",
                DeprecationWarning,
                stacklevel=2,
            )
        self.unloaded = unloaded
        # find env file
        dotenv.load_dotenv(env_file if env_file else dotenv.find_dotenv(usecwd=True))
        with Settings() as settings:
            cookie_jar = CookieJar()
            super().__init__(
                cookies=cookie_jar,
                headers={"User-Agent": f'python-ipfabric-sdk/{metadata.version("ipfabric")}'},
                **self._httpx_kwargs(kwargs, kwargs.get("verify", settings.verify), settings.timeout),
            )
            base_url = base_url or settings.url
            if not base_url:
                raise RuntimeError("IP Fabric base_url not provided or IPF_URL not set")

            self.api_version, self.os_version = self.check_version(api_version or settings.version, base_url)
            self.base_url = urljoin(base_url, f"api/{self.api_version}/")
            snapshot_id = snapshot_id or settings.snapshot
            if auth:
                token, username, password = None, None, None
            else:
                token = kwargs.get("token", settings.token)  # TODO: Update this in v7.0
                username = kwargs.get("username", settings.username)
                password = kwargs.get("password", settings.password)

        if token:
            self._login(token)
        elif username and password:
            self._login((username, password), base_url=base_url, cookie_jar=cookie_jar)
        else:
            self._login(auth, base_url=base_url, cookie_jar=cookie_jar)  # TODO: Keep only this in v7.0

        # Get Current User, by doing that we are also ensuring the token is valid
        self.user = self.get_user()
        self.snapshots = self.get_snapshots()
        self.oas = self._get_oas(base_url)
        self.streaming = streaming
        self._attribute_filters = None
        self._no_loaded_snapshots = False
        self.snapshot_id = snapshot_id
        logger.debug(
            f"Successfully connected to '{self.base_url.host}' IPF version '{self.os_version}' "
            f"as user '{self.user.username}'"
        )

    @property
    def _api_insuf_rights(self):
        msg = f'API_INSUFFICIENT_RIGHTS for user "{self.user.username}" '
        if self.user.token:
            msg += f'token "{self.user.token.description}" '
        return msg

    @property
    def hostname(self):
        resp = self.get("/os/hostname")
        if resp.status_code == 200:
            return resp.json()["hostname"]
        elif resp.status_code == 403:
            logger.critical(self._api_insuf_rights + 'on GET "/os/hostname".')
            return None
        else:
            resp.raise_for_status()

    @property
    def web_to_api(self):
        return {v.web_endpoint: v for k, v in self.oas.items() if v.web_endpoint}

    def _get_oas(self, base_url: str) -> Dict[str, OAS]:
        try:
            oas = {k: OAS(**v) for k, v in json.loads(OAS_DIR.joinpath(self.api_version + ".json").read_text()).items()}
            return oas
        except FileNotFoundError:
            return self._parse_oas(base_url)

    def _parse_oas(self, base_url) -> Dict[str, OAS]:
        resp = self.get(urljoin(base_url, "/api/oas/openapi-extended.json"))
        resp.raise_for_status()

        endpoints = dict()
        for endpoint, methods in resp.json()["paths"].items():
            data = OAS(api_endpoint=endpoint[1:])
            if "post" not in methods:
                continue
            try:
                data.web_endpoint = methods["post"]["x-table"]["webPath"]
            except KeyError:
                pass
            try:
                columns = set(
                    methods["post"]["requestBody"]["content"]["application/json"]["schema"]["properties"]["columns"][
                        "items"
                    ]["enum"]
                )
                data.columns = list(columns)
            except KeyError:
                pass
            try:
                columns = methods["post"]["responses"]["200"]["content"]["application/json"]["schema"]["properties"][
                    "data"
                ]["items"]["properties"]
                data.nested_columns = [k for k, v in columns.items() if "type" in v and v["type"] == "array"]
            except KeyError:
                pass
            endpoints[endpoint[1:]] = data

        return endpoints

    @staticmethod
    def _httpx_kwargs(kwargs: dict, verify: Any, timeout: Optional[int]):
        httpx_kwargs = kwargs.copy()
        # TODO: Remove 'token', 'username', 'password' in v7.0
        [httpx_kwargs.pop(h, None) for h in ["cookies", "token", "username", "password"]]
        httpx_kwargs["verify"] = verify
        if "timeout" not in kwargs and timeout:
            httpx_kwargs["timeout"] = timeout
        return httpx_kwargs

    def _login(self, auth: Any, base_url: str = None, cookie_jar: CookieJar = None):
        if not auth:
            raise RuntimeError("IP Fabric Authentication not provided.")
        elif isinstance(auth, str):
            self.headers.update({"X-API-Token": auth})
        elif isinstance(auth, tuple):
            resp = self.post("auth/login", json=dict(username=auth[0], password=auth[1]))
            resp.raise_for_status()
            self.auth = AccessToken(httpx.Client(base_url=base_url, cookies=cookie_jar))
        else:
            self.auth = auth

    @property
    def attribute_filters(self):
        return self._attribute_filters

    @attribute_filters.setter
    def attribute_filters(self, attribute_filters: Union[Dict[str, List[str]], None]):
        if attribute_filters:
            logger.warning(
                "Setting Global Attribute Filter for all tables/diagrams until explicitly unset to None.\n"
                "Adding an Attribute Filter to any function will overwrite the Global Filter.\n"
                f"Filter: {attribute_filters}"
            )
        self._attribute_filters = attribute_filters

    def get_user(self) -> User:
        """Gets current logged in user information.

        Returns:
            User: User model of logged in user
        """
        resp = self.get("users/me")
        resp.raise_for_status()
        return User(**resp.json())

    def check_version(self, api_version: str = None, base_url: Union[URL, str] = None) -> tuple:
        """Checks API Version and returns the version to use in the URL and the OS Version

        Args:
            api_version: User defined API Version or None
            base_url: URL of IP Fabric

        Returns:
            api_version, os_version
        """
        api_version = (
            api_version.lstrip("v").split(".") if api_version else metadata.version("ipfabric").lstrip("v").split(".")
        )

        resp = self.get(URL(base_url or self.base_url).join("/api/version"))
        resp.raise_for_status()
        os_api_version = resp.json()["apiVersion"].lstrip("v").split(".")
        return_version = f"v{api_version[0]}.{api_version[1]}" if len(api_version) > 1 else f"v{api_version[0]}"
        if len(api_version) == 1 and api_version[0] > os_api_version[0]:
            logger.warning(
                f"Specified API or SDK Version (v{api_version[0]}) is greater then "
                f"OS API Version. Using OS Version:  (v{os_api_version[0]})"
            )
            return_version = f"v{os_api_version[0]}"
        elif api_version[0:2] > os_api_version[0:2]:
            logger.warning(
                f"Specified API or SDK Version (v{'.'.join(api_version)}) is greater then "
                f"OS API Version. Using OS Version:  (v{'.'.join(os_api_version)})"
            )
            return_version = f"v{os_api_version[0]}.{os_api_version[1]}"
        elif os_api_version[0] > api_version[0]:
            raise RuntimeError(
                f"OS Major Version v{os_api_version[0]} is greater then SDK Version "
                f"v{api_version[0]}.  Please upgrade the Python SDK to the new major version."
            )

        return return_version, resp.json()["releaseVersion"]

    def update(self):
        """get all snapshots and assigns them to an attribute"""
        self.snapshots = self.get_snapshots()
        self._no_loaded_snapshots = self.loaded_snapshots == dict()

    @property
    def loaded_snapshots(self) -> Dict[str, Snapshot]:
        """get only loaded snapshots"""
        return {k: v for k, v in self.snapshots.items() if v.loaded}

    @property
    def unloaded_snapshots(self) -> Dict[str, Snapshot]:
        if not self.unloaded:
            logger.warning("Unloaded snapshots not initialized. Retrieving unloaded snapshots.")
            self.unloaded = True
            self.update()
        return {k: v for k, v in self.snapshots.items() if not v.loaded}

    @property
    def snapshot_id(self) -> str:
        """get snapshot Id"""
        return self._snapshot_id

    @property
    def snapshot(self) -> Snapshot:
        return self.snapshots[self.snapshot_id]

    @snapshot_id.setter
    def snapshot_id(self, snapshot_id):
        snapshot_id = snapshot_id or LAST_ID
        if not self.loaded_snapshots:
            logger.warning("No Snapshots are currently loaded.  Please load a snapshot before querying any data.")
            self._snapshot_id = None
            self._no_loaded_snapshots = True
        elif snapshot_id not in self.snapshots:
            # Verify snapshot ID is valid
            raise ValueError(f"Incorrect Snapshot ID: '{snapshot_id}'")
        else:
            self._snapshot_id = self.snapshots[snapshot_id].snapshot_id

    def get_snapshot(self, snapshot_id: str):
        if snapshot_id in self.snapshots:
            return self.snapshots[snapshot_id]
        else:
            if self.api_version < "v6.3":  # TODO: Remove v7.0
                SNAPSHOT_COLUMNS.discard("creatorUsername")
            payload = {"columns": list(SNAPSHOT_COLUMNS), "filters": {"id": ["eq", snapshot_id]}}
            results = self._ipf_pager("tables/management/snapshots", payload)
            if not results:
                logger.error(f"Snapshot {snapshot_id} not found.")
                return None
            get_results = self._get_snapshots()
            snapshot = self._create_snapshot_model(results[0], get_results)
            if snapshot.loaded:
                snapshot.get_assurance_engine_settings(self)
            return snapshot

    @staticmethod
    def _create_snapshot_model(s, get_results):
        return Snapshot(
            **s,
            licensedDevCount=get_results[s["id"]].get("licensedDevCount", None),
            errors=get_results[s["id"]].get("errors", None),
            version=get_results[s["id"]]["version"],
            initialVersion=get_results[s["id"]].get("initialVersion", None),
        )

    def get_snapshot_id(self, snapshot: Union[Snapshot, str]):
        """
        Returns a Snapshot ID for a given input.

        Args:
            snapshot: Snapshot model, name, or ID

        Returns:
            Snapshot ID
        """
        if isinstance(snapshot, Snapshot):
            return snapshot.snapshot_id
        elif snapshot in VALID_REFS:
            return self.snapshots[snapshot].snapshot_id
        try:
            UUID(snapshot, version=4)
            return self.snapshots[snapshot].snapshot_id
        except ValueError:
            for snap in list(self.snapshots.values()):
                if snapshot == snap.name:
                    return snap.snapshot_id
        raise ValueError(f"Could not locate Snapshot ID for {snapshot}.")

    def _get_snapshots(self):
        """
        Need to do a GET and POST to get all Snapshot data. See NIM-7223
        POST Missing:
        licensedDevCount
        errors
        version
        initialVersion
        """
        res = self.get("/snapshots")
        res.raise_for_status()
        return {s["id"]: s for s in res.json()}

    def get_snapshots(self) -> Dict[str, Snapshot]:
        """Gets all snapshots from IP Fabric and returns a dictionary of {ID: Snapshot_info}

        Returns:
            Dictionary with ID as key and dictionary with info as the value
        """
        if self.api_version < "v6.3":  # TODO: Remove v7.0
            SNAPSHOT_COLUMNS.discard("creatorUsername")
        payload = {"columns": list(SNAPSHOT_COLUMNS), "sort": {"order": "desc", "column": "tsEnd"}}
        if not self.unloaded:
            logger.warning("Retrieving only loaded snapshots. To load all snapshots set `unloaded` to True.")
            payload["filters"] = {"and": [{"status": ["eq", "done"]}, {"finishStatus": ["eq", "done"]}]}
        results = self._ipf_pager("tables/management/snapshots", payload)
        get_results = self._get_snapshots()

        snap_dict = OrderedDict()
        for s in results:
            snap = self._create_snapshot_model(s, get_results)
            snap_dict[snap.snapshot_id] = snap
            if snap.loaded:
                snap.get_assurance_engine_settings(self)
                if LASTLOCKED_ID not in snap_dict and snap.locked:
                    snap_dict[LASTLOCKED_ID] = snap
                if LAST_ID not in snap_dict:
                    snap_dict[LAST_ID] = snap
                    continue
                if PREV_ID not in snap_dict:
                    snap_dict[PREV_ID] = snap
        return snap_dict

    def _ipf_pager(
        self,
        url: str,
        payload: dict,
        limit: int = 1000,
        start: int = 0,
    ):
        """
        Loops through and collects all the data from the tables
        :param url: str: Full URL to post to
        :param payload: dict: Data to submit to IP Fabric
        :param start: int: Where to start for the data
        :return: list: List of dictionaries
        """
        payload["pagination"] = dict(limit=limit)
        data = list()

        def page(s):
            payload["pagination"]["start"] = s
            r = self.post(url, json=payload)
            r.raise_for_status()
            return r.json()["data"]

        r_data = page(start)
        data.extend(r_data)
        while limit == len(r_data):
            start = start + limit
            r_data = page(start)
            data.extend(r_data)
        return data

    def trigger_backup(self, sn: str = None, ip: str = None):
        if sn:
            payload = {"sn": sn}
        else:
            try:
                ip = str(IPv4Address(ip))
            except AddressValueError:
                raise ValueError(f"Invalid IP Address, CIDR is not allowed: {ip}")
            payload = {"ip": ip}
        res = self.post("/discovery/trigger-config-backup", json=payload)
        res.raise_for_status()
        return res.status_code
