import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Qos(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def policy_maps(self):
        return models.Table(client=self.client, endpoint="tables/qos/policy-maps", sn=self.sn)

    @property
    def shaping(self):
        return models.Table(client=self.client, endpoint="tables/qos/shaping", sn=self.sn)

    @property
    def queuing(self):
        return models.Table(client=self.client, endpoint="tables/qos/queuing", sn=self.sn)

    @property
    def policing(self):
        return models.Table(client=self.client, endpoint="tables/qos/policing", sn=self.sn)

    @property
    def priority_queuing(self):
        return models.Table(client=self.client, endpoint="tables/qos/priority-queuing", sn=self.sn)

    @property
    def marking(self):
        return models.Table(client=self.client, endpoint="tables/qos/marking", sn=self.sn)

    @property
    def random_drops(self):
        return models.Table(client=self.client, endpoint="tables/qos/random-drops", sn=self.sn)
