import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Vlans(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def device_summary(self):
        return models.Table(client=self.client, endpoint="tables/vlan/device-summary", sn=self.sn)

    @property
    def device_detail(self):
        return models.Table(client=self.client, endpoint="tables/vlan/device", sn=self.sn)

    @property
    def network_summary(self):
        return models.Table(client=self.client, endpoint="tables/vlan/network-summary", sn=self.sn)

    @property
    def site_summary(self):
        return models.Table(client=self.client, endpoint="tables/vlan/site-summary", sn=self.sn)

    @property
    def l3_gateways(self):
        return models.Table(client=self.client, endpoint="tables/vlan/l3-gateways", sn=self.sn)
