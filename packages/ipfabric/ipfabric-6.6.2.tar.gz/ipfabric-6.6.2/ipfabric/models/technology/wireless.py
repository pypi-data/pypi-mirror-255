import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Wireless(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def controllers(self):
        return models.Table(client=self.client, endpoint="tables/wireless/controllers", sn=self.sn)

    @property
    def access_points(self):
        return models.Table(client=self.client, endpoint="tables/wireless/access-points", sn=self.sn)

    @property
    def radios_detail(self):
        return models.Table(client=self.client, endpoint="tables/wireless/radio", sn=self.sn)

    @property
    def radios_ssid_summary(self):
        return models.Table(client=self.client, endpoint="tables/wireless/ssid-summary", sn=self.sn)

    @property
    def clients(self):
        return models.Table(client=self.client, endpoint="tables/wireless/clients", sn=self.sn)
