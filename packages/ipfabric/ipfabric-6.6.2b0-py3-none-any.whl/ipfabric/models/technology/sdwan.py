import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Sdwan(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def sites(self):
        return models.Table(client=self.client, endpoint="tables/sdwan/sites", sn=self.sn)

    @property
    def links(self):
        return models.Table(client=self.client, endpoint="tables/sdwan/links", sn=self.sn)
