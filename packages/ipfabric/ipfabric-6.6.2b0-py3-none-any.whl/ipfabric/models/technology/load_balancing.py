import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class LoadBalancing(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def virtual_servers(self):
        return models.Table(client=self.client, endpoint="tables/load-balancing/virtual-servers", sn=self.sn)

    @property
    def virtual_servers_pools(self):
        return models.Table(client=self.client, endpoint="tables/load-balancing/virtual-servers/pools", sn=self.sn)

    @property
    def virtual_servers_pool_members(self):
        return models.Table(
            client=self.client, endpoint="tables/load-balancing/virtual-servers/pool-members", sn=self.sn
        )

    @property
    def virtual_servers_f5_partitions(self):
        return models.Table(client=self.client, endpoint="tables/load-balancing/f5-partitions", sn=self.sn)
