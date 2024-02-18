import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Fhrp(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def group_state(self):
        return models.Table(client=self.client, endpoint="tables/fhrp/group-state", sn=self.sn)

    @property
    def group_members(self):
        return models.Table(client=self.client, endpoint="tables/fhrp/group-members", sn=self.sn)

    @property
    def stproot_alignment(self):
        return models.Table(client=self.client, endpoint="tables/fhrp/stproot-alignment", sn=self.sn)

    @property
    def balancing(self):
        return models.Table(client=self.client, endpoint="tables/fhrp/balancing", sn=self.sn)

    @property
    def glbp_forwarders(self):
        return models.Table(client=self.client, endpoint="tables/fhrp/glbp-forwarders", sn=self.sn)

    @property
    def virtual_gateways(self):
        return models.Table(client=self.client, endpoint="tables/fhrp/virtual-gateways", sn=self.sn)
