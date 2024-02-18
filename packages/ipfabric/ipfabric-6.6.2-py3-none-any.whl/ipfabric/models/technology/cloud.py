import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Cloud(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def virtual_machines(self):
        return models.Table(client=self.client, endpoint="tables/cloud/virtual-machines", sn=self.sn)

    @property
    def virtual_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/cloud/virtual-machines-interfaces", sn=self.sn)
