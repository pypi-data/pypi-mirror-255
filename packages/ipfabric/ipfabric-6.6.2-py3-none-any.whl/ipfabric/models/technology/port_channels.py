import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class PortChannels(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def inbound_balancing_table(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/port-channel/balance/inbound", sn=self.sn)

    @property
    def outbound_balancing_table(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/port-channel/balance/outbound", sn=self.sn)

    @property
    def member_status_table(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/port-channel/member-status", sn=self.sn)

    @property
    def mlag_switches(self):
        return models.Table(client=self.client, endpoint="tables/platforms/mlag/switches", sn=self.sn)

    @property
    def mlag_peers(self):
        return models.Table(client=self.client, endpoint="tables/platforms/mlag/peers", sn=self.sn)

    @property
    def mlag_pairs(self):
        return models.Table(client=self.client, endpoint="tables/platforms/mlag/pairs", sn=self.sn)

    @property
    def mlag_cisco_vpc(self):
        return models.Table(client=self.client, endpoint="tables/platforms/mlag/vpc", sn=self.sn)
