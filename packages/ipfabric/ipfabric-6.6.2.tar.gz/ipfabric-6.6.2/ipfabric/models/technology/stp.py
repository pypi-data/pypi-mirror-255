import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Stp(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def bridges(self):
        return models.Table(client=self.client, endpoint="tables/spanning-tree/bridges", sn=self.sn)

    @property
    def instances(self):
        return models.Table(client=self.client, endpoint="tables/spanning-tree/instances", sn=self.sn)

    @property
    def vlans(self):
        return models.Table(client=self.client, endpoint="tables/spanning-tree/vlans", sn=self.sn)

    @property
    def ports(self):
        return models.Table(client=self.client, endpoint="tables/spanning-tree/ports", sn=self.sn)

    @property
    def neighbors(self):
        return models.Table(client=self.client, endpoint="tables/spanning-tree/neighbors", sn=self.sn)

    @property
    def guards(self):
        return models.Table(client=self.client, endpoint="tables/spanning-tree/guards", sn=self.sn)

    @property
    def inconsistencies(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/inconsistencies/summary", sn=self.sn)

    @property
    def inconsistencies_details(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/inconsistencies/details", sn=self.sn)

    @property
    def inconsistencies_ports_vlan_mismatch(self):
        return models.Table(
            client=self.client, endpoint="tables/spanning-tree/inconsistencies/neighbor-ports-vlan-mismatch", sn=self.sn
        )

    @property
    def inconsistencies_ports_multiple_neighbors(self):
        return models.Table(
            client=self.client, endpoint="tables/spanning-tree/inconsistencies/ports-multiple-neighbors", sn=self.sn
        )

    @property
    def inconsistencies_stp_cdp_ports_mismatch(self):
        return models.Table(
            client=self.client, endpoint="tables/spanning-tree/inconsistencies/stp-cdp-ports-mismatch", sn=self.sn
        )

    @property
    def inconsistencies_multiple_stp(self):
        return models.Table(
            client=self.client, endpoint="tables/spanning-tree/inconsistencies/multiple-stp", sn=self.sn
        )
