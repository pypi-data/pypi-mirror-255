import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Dhcp(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def relay_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/dhcp/relay/interfaces", sn=self.sn)

    @property
    def relay_interfaces_stats_received(self):
        return models.Table(client=self.client, endpoint="tables/dhcp/relay/interfaces-stats/received", sn=self.sn)

    @property
    def relay_interfaces_stats_relayed(self):
        return models.Table(client=self.client, endpoint="tables/dhcp/relay/interfaces-stats/relayed", sn=self.sn)

    @property
    def relay_interfaces_stats_sent(self):
        return models.Table(client=self.client, endpoint="tables/dhcp/relay/interfaces-stats/sent", sn=self.sn)

    @property
    def relay_global_stats_summary(self):
        return models.Table(client=self.client, endpoint="tables/dhcp/relay/global-stats/summary", sn=self.sn)

    @property
    def relay_global_stats_received(self):
        return models.Table(client=self.client, endpoint="tables/dhcp/relay/global-stats/received", sn=self.sn)

    @property
    def relay_global_stats_relayed(self):
        return models.Table(client=self.client, endpoint="tables/dhcp/relay/global-stats/relayed", sn=self.sn)

    @property
    def relay_global_stats_sent(self):
        return models.Table(client=self.client, endpoint="tables/dhcp/relay/global-stats/sent", sn=self.sn)

    @property
    def server_summary(self):
        return models.Table(client=self.client, endpoint="tables/dhcp/server/summary", sn=self.sn)

    @property
    def server_pools(self):
        return models.Table(client=self.client, endpoint="tables/dhcp/server/pools", sn=self.sn)

    @property
    def server_leases(self):
        return models.Table(client=self.client, endpoint="tables/dhcp/server/leases", sn=self.sn)

    @property
    def server_excluded_ranges(self):
        return models.Table(client=self.client, endpoint="tables/dhcp/server/excluded-ranges", sn=self.sn)

    @property
    def server_excluded_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/dhcp/server/interfaces", sn=self.sn)
