import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Neighbors(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def neighbors_all(self):
        return models.Table(client=self.client, endpoint="tables/neighbors/all", sn=self.sn)

    @property
    def neighbors_unmanaged(self):
        return models.Table(client=self.client, endpoint="tables/neighbors/unmanaged", sn=self.sn)

    @property
    def neighbors_unidirectional(self):
        return models.Table(client=self.client, endpoint="tables/neighbors/unidirectional", sn=self.sn)

    @property
    def neighbors_endpoints(self):
        return models.Table(client=self.client, endpoint="tables/neighbors/endpoints", sn=self.sn)
