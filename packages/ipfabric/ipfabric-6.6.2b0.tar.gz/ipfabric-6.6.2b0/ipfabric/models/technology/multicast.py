import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Multicast(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def pim_neighbors(self):
        return models.Table(client=self.client, endpoint="tables/multicast/pim/neighbors", sn=self.sn)

    @property
    def pim_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/multicast/pim/interfaces", sn=self.sn)

    @property
    def mroute_overview(self):
        return models.Table(client=self.client, endpoint="tables/multicast/routes/overview", sn=self.sn)

    @property
    def mroute_table(self):
        return models.Table(client=self.client, endpoint="tables/multicast/routes/table", sn=self.sn)

    @property
    def mroute_oil_detail(self):
        return models.Table(client=self.client, endpoint="tables/multicast/routes/outgoing-interfaces", sn=self.sn)

    @property
    def mroute_counters(self):
        return models.Table(client=self.client, endpoint="tables/multicast/routes/counters", sn=self.sn)

    @property
    def mroute_first_hop_router(self):
        return models.Table(client=self.client, endpoint="tables/multicast/routes/first-hop-router", sn=self.sn)

    @property
    def mroute_sources(self):
        return models.Table(client=self.client, endpoint="tables/multicast/routes/sources", sn=self.sn)

    @property
    def igmp_groups(self):
        return models.Table(client=self.client, endpoint="tables/multicast/igmp/groups", sn=self.sn)

    @property
    def igmp_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/multicast/igmp/interfaces", sn=self.sn)

    @property
    def igmp_snooping_global_config(self):
        return models.Table(client=self.client, endpoint="tables/multicast/igmp/snooping/global", sn=self.sn)

    @property
    def igmp_snooping_groups(self):
        return models.Table(client=self.client, endpoint="tables/multicast/igmp/snooping/groups", sn=self.sn)

    @property
    def igmp_snooping_vlans(self):
        return models.Table(client=self.client, endpoint="tables/multicast/igmp/snooping/vlans", sn=self.sn)

    @property
    def mac_table(self):
        return models.Table(client=self.client, endpoint="tables/multicast/mac", sn=self.sn)

    @property
    def rp_overview(self):
        return models.Table(client=self.client, endpoint="tables/multicast/pim/rp/overview", sn=self.sn)

    @property
    def rp_bsr(self):
        return models.Table(client=self.client, endpoint="tables/multicast/pim/rp/bsr", sn=self.sn)

    @property
    def rp_mappings(self):
        return models.Table(client=self.client, endpoint="tables/multicast/pim/rp/mappings", sn=self.sn)

    @property
    def rp_mappings_groups(self):
        return models.Table(client=self.client, endpoint="tables/multicast/pim/rp/mappings-groups", sn=self.sn)
