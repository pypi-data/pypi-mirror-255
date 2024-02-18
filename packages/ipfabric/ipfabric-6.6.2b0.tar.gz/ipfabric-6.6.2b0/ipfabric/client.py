import json
import logging
import re
from json import loads, dumps
from typing import Optional, Union, Dict, List, Any, overload, Literal
from urllib.parse import urlparse, urljoin
from warnings import warn

from httpx import HTTPStatusError, InvalidURL

from ipfabric.api import IPFabricAPI
from ipfabric.diagrams import Diagram
from ipfabric.models import Technology, Inventory, Jobs, Intent, Devices
from ipfabric.tools import TIMEZONES

try:
    from pandas import DataFrame
except ImportError:
    DataFrame = None

logger = logging.getLogger("ipfabric")

RE_PATH = re.compile(r"^/?(api/)?v\d(\.\d)?/")
RE_TABLE = re.compile(r"^tables/")
EXPORT_FORMAT = Literal["json", "csv", "df"]


class IPFClient(IPFabricAPI):
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
            streaming: Stream table requests instead of paging results, see documentation for important information.
            **kwargs: Keyword args to pass to httpx
        """
        super().__init__(
            base_url=base_url,
            api_version=api_version,
            auth=auth,
            snapshot_id=snapshot_id,
            unloaded=unloaded,
            env_file=env_file,
            streaming=streaming,
            **kwargs,
        )
        if self.streaming and self.os_version.split("+")[0] < "6.3.1":
            logger.warning(
                f"Setting `streaming=True` is not recommended until 6.3.1 due to RBAC issues: "  # TODO: Remove in v7.0
                f"IP Fabric OS Version is {self.os_version}."
            )
        self.inventory = Inventory(client=self)
        self.technology = Technology(client=self)
        self.jobs = Jobs(client=self)
        self.diagram = Diagram(ipf=self)
        self.intent = Intent(client=self, load=False)
        self._devices = list()

    @property
    def snapshot_id(self) -> str:
        """get snapshot Id"""
        return self._snapshot_id

    @snapshot_id.setter
    def snapshot_id(self, snapshot_id):
        super(self.__class__, self.__class__).snapshot_id.fset(self, snapshot_id)
        if self.snapshot.disabled_intent_verification is False:
            self.intent = Intent(client=self)
        self.inventory = Inventory(client=self)
        self._devices = self.load_devices()

    @property
    def devices(self) -> Devices:
        """get devices"""
        if not self._devices:
            logger.info("Devices not loaded, loading devices.")
            self._devices = self.load_devices()
        return self._devices

    @devices.setter
    def devices(self, devices):
        self._devices = devices

    def load_devices(self, device_filters: dict = None, device_attr_filters: dict = None):
        if self._no_loaded_snapshots:
            logger.warning("No loaded snapshots, cannot load devices.")
        else:
            if not device_attr_filters and self.attribute_filters:
                logger.warning(
                    f"Global `attribute_filters` is set; only pulling devices matching:\n{self.attribute_filters}."
                )
            try:
                self.devices = self.inventory.devices.all(
                    export="object", filters=device_filters, attr_filters=device_attr_filters
                )
                return self.devices
            except HTTPStatusError:
                logger.warning(self._api_insuf_rights + 'on POST "/tables/inventory/devices". Will not load Devices.')
        return list()

    def _check_url(self, url):
        path = urlparse(url).path
        path = path if path[0] == "/" else "/" + path
        if path in self.web_to_api:
            return self.web_to_api[path].api_endpoint
        r = RE_PATH.search(path)
        url = path[r.end():] if r else path  # fmt: skip
        url = url[1:] if url[0] == "/" else url
        return url

    def _create_payload(self, url, snapshot_id, filters, sort, attr_filters):
        payload = dict()
        if self.api_version >= "v6.3":  # TODO: No check in v7.0
            payload = {"format": {"dataType": "json"}}
        if filters and isinstance(filters, str):
            payload["filters"] = loads(filters)
        elif filters and isinstance(filters, dict):
            payload["filters"] = filters
        if snapshot_id:
            payload["snapshot"] = snapshot_id
        if sort:
            payload["sort"] = sort
        if RE_TABLE.match(url) and (attr_filters or self.attribute_filters):
            payload["attributeFilters"] = attr_filters or self.attribute_filters
        return payload

    def _check_url_payload(self, url, snapshot_id, filters, reports, sort, attr_filters, export, csv_tz):
        url = self._check_url(url)
        payload = self._create_payload(url, snapshot_id, filters, sort, attr_filters)

        if export != "csv":
            if isinstance(reports, (str, list)):
                payload["reports"] = reports
            elif reports is True and self.oas.get(url, None) and self.oas[url].web_endpoint:
                payload["reports"] = self.oas[url].web_endpoint
            elif reports is True and (not self.oas.get(url, None) or not self.oas[url].web_endpoint):
                logger.warning(
                    f"Could not automatically discover Web Endpoint for Intent Data for table '/{url}'.\n"
                    f"Returning results without Intent Rules."
                )
        else:
            if reports:
                logger.warning("CSV export does not return reports, parameter has been excluded.")
            payload["format"] = {"exportToFile": True, "dataType": "csv"}
            if csv_tz and csv_tz.lower() not in TIMEZONES:
                raise ValueError(
                    f"CSV timezone '{csv_tz}' not in available timezones; see `ipfabric.tools.shared.TIMEZONES`"
                )
            elif csv_tz:
                payload["format"]["options"] = {"timezone": TIMEZONES[csv_tz.lower()]}
        return url, payload

    def _get_payload(self, url, payload):
        snapshot_id = payload.pop("snapshot", None)
        reports = payload.pop("reports") if "reports" in payload and isinstance(payload["reports"], str) else None
        p = "&".join([f"{k}={dumps(v, separators=(',', ':'))}" for k, v in payload.items()])
        if snapshot_id:
            p += f"&snapshot={snapshot_id}"
        if reports:
            p += f"&reports={reports}"
        url = urljoin(str(self.base_url), url + f"?{p}")
        if len(url) > 4096:
            return False
        return url

    def _stream(self, url, payload, export):
        if export == "csv" and self.api_version < "v6.3":
            raise NotImplementedError(f"CSV export is implemented in v6.3.0; IPF version: {self.os_version}.")
        get_url = self._get_payload(url, payload)
        if get_url is False and export == "csv":
            raise InvalidURL("URL exceeds max character limit of 4096 cannot export to CSV.")
        elif get_url is False:
            logger.warning("URL exceeds max character limit of 4096 switching to pagination.")
            return False
        with self.stream("GET", get_url) as stream_resp:
            stream_resp.raise_for_status()
            data = stream_resp.read()
        return data if export == "csv" else loads(data)["data"]

    def query(self, url: str, payload: Union[str, dict], get_all: bool = True) -> Union[List[dict], bytes]:
        """Submits a query, does no formatting on the parameters.  Use for copy/pasting from the webpage.

        Args:
            url: Example: https://demo1.ipfabric.io/api/v1/tables/vlan/device-summary or tables/vlan/device-summary
            payload: Dictionary to submit in POST or can be JSON string (i.e. read from file).
            get_all: Default use pager to get all results and ignore pagination information in the payload

        Returns:
            list or bytes: List of Dictionary objects or bytes if csv.
        """
        url = self._check_url(url)
        if isinstance(payload, str):
            payload = loads(payload)
        export = payload.get("format", {}).get("dataType", "json")
        data = False
        if export == "csv" or (self.streaming and get_all):
            data = self._stream(url, payload, export)
        elif get_all and data is False:
            data = self._ipf_pager(url, payload)
        elif data is False:
            res = self.post(url, json=payload)
            res.raise_for_status()
            data = res.json()["data"]
        return data

    def _get_columns(self, url: str):  # TODO: Remove in v7
        warn("This method will be removed in v7.0, please use `get_columns`.", DeprecationWarning, stacklevel=2)
        return self.get_columns(url=url)

    def get_columns(self, url: str) -> List[str]:
        """Checks OAS to find available columns.

        Args:
            url: API url to post

        Returns:
            list: List of column names
        """
        if self.oas.get(url, None) and self.oas[url].columns:
            return self.oas[url].columns
        else:
            raise LookupError(f"Could not find columns for table '/{url}'.")

    def get_count(
        self,
        url: str,
        filters: Optional[Union[dict, str]] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot_id: Optional[str] = None,
        snapshot: bool = True,
    ) -> int:
        """Get a total number of rows
        Args:
            url: API URL to post to
            filters: Optional dictionary of filters
            attr_filters: Optional dictionary of attribute filters
            snapshot_id: Optional snapshot_id to override default
            snapshot: Set to False for some tables like management endpoints.
        Returns:
            int: a count of rows
        """
        snapshot_id = snapshot_id or self.snapshot_id if snapshot else None
        url, payload = self._check_url_payload(url, snapshot_id, filters, None, None, attr_filters, None, None)
        payload.update({"columns": ["id"], "pagination": {"limit": 1, "start": 0}})
        res = self.post(url, json=payload)
        res.raise_for_status()
        return res.json()["_meta"]["count"]

    def _fetch_setup(self, url, export, columns, snapshot_id, filters, reports, sort, attr_filters, csv_tz, snapshot):
        if export == "df" and DataFrame is None:
            raise ImportError("pandas not installed. Run `pip install ipfabric[pd]`.")
        snapshot_id = snapshot_id or self.snapshot_id if snapshot else None
        if "color" in json.dumps(filters) and not reports:
            reports = True
        url, payload = self._check_url_payload(url, snapshot_id, filters, reports, sort, attr_filters, export, csv_tz)
        payload["columns"] = columns or self.get_columns(url)
        return url, payload

    @overload
    def fetch(
        self,
        url,
        export: Literal["json"] = ...,
        columns: Optional[List] = None,
        filters: Optional[Union[dict, str]] = None,
        limit: Optional[int] = 1000,
        start: Optional[int] = 0,
        snapshot_id: Optional[str] = None,
        reports: Optional[Union[bool, list, str]] = False,
        sort: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot: bool = True,
    ) -> List[dict]: ...

    @overload
    def fetch(
        self,
        url,
        export: Literal["csv"],
        columns: Optional[List] = None,
        filters: Optional[Union[dict, str]] = None,
        limit: Optional[int] = 1000,
        start: Optional[int] = 0,
        snapshot_id: Optional[str] = None,
        sort: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot: bool = True,
        csv_tz: Optional[str] = None,
    ) -> bytes: ...

    @overload
    def fetch(
        self,
        url,
        export: Literal["df"] = ...,
        columns: Optional[List] = None,
        filters: Optional[Union[dict, str]] = None,
        limit: Optional[int] = 1000,
        start: Optional[int] = 0,
        snapshot_id: Optional[str] = None,
        reports: Optional[Union[bool, list, str]] = False,
        sort: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot: bool = True,
    ) -> DataFrame: ...

    def fetch(
        self,
        url,
        export: EXPORT_FORMAT = "json",
        columns: Optional[List] = None,
        filters: Optional[Union[dict, str]] = None,
        limit: Optional[int] = 1000,
        start: Optional[int] = 0,
        snapshot_id: Optional[str] = None,
        reports: Optional[Union[bool, list, str]] = False,
        sort: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot: bool = True,
        csv_tz: Optional[str] = None,
    ):
        """Gets data from IP Fabric for specified endpoint

        Args:
            url: Example tables/vlan/device-summary
            export: str: Export format to return [json, csv]; default is json.
            columns: Optional list of columns to return, None will return all
            filters: Optional dictionary of filters
            limit: Default to 1,000 rows
            start: Starts at 0
            snapshot_id: Optional snapshot_id to override default
            reports: String of frontend URL where the reports are displayed or a list of report IDs
            sort: Dictionary to apply sorting: {"order": "desc", "column": "lastChange"}
            attr_filters: Optional dictionary to apply an Attribute filter
            snapshot: Set to False for some tables like management endpoints.
            csv_tz: str: Default None, set a timezone to return human-readable dates when using CSV;
                         see `ipfabric.tools.shared.TIMEZONES`
        Returns:
            Union[List[dict], bytes, pandas.DataFrame]: List of dict if json, bytes string if CSV, DataFrame is df
        """
        url, payload = self._fetch_setup(
            url, export, columns, snapshot_id, filters, reports, sort, attr_filters, csv_tz, snapshot
        )
        payload["pagination"] = dict(start=start, limit=limit)
        data = False
        if export == "csv" or self.streaming:
            data = self._stream(url, payload, export)
        if data is False:
            res = self.post(url, json=payload)
            res.raise_for_status()
            data = res.json()["data"]
        if export == "df":
            data = DataFrame.from_records(data) if export == "df" else data
        return data

    @overload
    def fetch_all(
        self,
        url: str,
        export: Literal["json"] = ...,
        columns: Optional[List] = None,
        filters: Optional[Union[dict, str]] = None,
        snapshot_id: Optional[str] = None,
        reports: Optional[Union[bool, list, str]] = False,
        sort: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot: bool = True,
    ) -> List[dict]: ...

    @overload
    def fetch_all(
        self,
        url: str,
        export: Literal["csv"],
        columns: Optional[List] = None,
        filters: Optional[Union[dict, str]] = None,
        snapshot_id: Optional[str] = None,
        sort: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot: bool = True,
        csv_tz: Optional[str] = None,
    ) -> bytes: ...

    @overload
    def fetch_all(
        self,
        url: str,
        export: Literal["df"],
        columns: Optional[List] = None,
        filters: Optional[Union[dict, str]] = None,
        snapshot_id: Optional[str] = None,
        reports: Optional[Union[bool, list, str]] = False,
        sort: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot: bool = True,
    ) -> DataFrame: ...

    def fetch_all(
        self,
        url: str,
        export: EXPORT_FORMAT = "json",
        columns: Optional[List] = None,
        filters: Optional[Union[dict, str]] = None,
        snapshot_id: Optional[str] = None,
        reports: Optional[Union[bool, list, str]] = False,
        sort: Optional[dict] = None,
        attr_filters: Optional[Dict[str, List[str]]] = None,
        snapshot: bool = True,
        csv_tz: Optional[str] = None,
    ):
        """Gets all data from IP Fabric for specified endpoint

        Args:
            url: Example tables/vlan/device-summary
            export: str: Export format to return [json, csv]; default is json.
            columns: Optional list of columns to return, None will return all
            filters: Optional dictionary of filters
            snapshot_id: Optional snapshot_id to override default
            reports: String of frontend URL where the reports are displayed or a list of report IDs
            sort: Optional dictionary to apply sorting: {"order": "desc", "column": "lastChange"}
            attr_filters: Optional dictionary to apply an Attribute filter
            snapshot: Set to False for some tables like management endpoints.
            csv_tz: str: Default None, set a timezone to return human-readable dates when using CSV;
                         see `ipfabric.tools.shared.TIMEZONES`
        Returns:
            Union[List[dict], bytes, pandas.DataFrame]: List of dict if json, bytes string if CSV, DataFrame is df
        """
        url, payload = self._fetch_setup(
            url, export, columns, snapshot_id, filters, reports, sort, attr_filters, csv_tz, snapshot
        )
        data = False
        if export == "csv" or self.streaming:
            data = self._stream(url, payload, export)
        if data is False:
            data = self._ipf_pager(url, payload)
        if export == "df":
            data = DataFrame.from_records(data)
        return data
