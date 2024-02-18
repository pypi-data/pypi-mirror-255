import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class ManagedNetworks(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def networks(self):
        return models.Table(client=self.client, endpoint="tables/networks", sn=self.sn)

    @property
    def gateway_redundancy(self):
        return models.Table(client=self.client, endpoint="tables/networks/gateway-redundancy", sn=self.sn)
