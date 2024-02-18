import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Platforms(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def environment_power_supplies(self):
        return models.Table(client=self.client, endpoint="tables/inventory/power-supplies", sn=self.sn)

    @property
    def environment_power_supplies_fans(self):
        return models.Table(client=self.client, endpoint="tables/inventory/power-supplies-fans", sn=self.sn)

    @property
    def environment_fans(self):
        return models.Table(client=self.client, endpoint="tables/inventory/fans", sn=self.sn)

    @property
    def environment_modules(self):
        return models.Table(client=self.client, endpoint="tables/inventory/modules", sn=self.sn)

    @property
    def environment_temperature_sensors(self):
        return models.Table(client=self.client, endpoint="tables/inventory/temperature-sensors", sn=self.sn)

    @property
    def cisco_fabric_path_summary(self):
        return models.Table(client=self.client, endpoint="tables/platforms/fabric-path/summary", sn=self.sn)

    @property
    def cisco_fabric_path_isis_neighbors(self):
        return models.Table(client=self.client, endpoint="tables/platforms/fabric-path/neighbors", sn=self.sn)

    @property
    def cisco_fabric_path_switches(self):
        return models.Table(client=self.client, endpoint="tables/platforms/fabric-path/switches", sn=self.sn)

    @property
    def cisco_fabric_path_routes(self):
        return models.Table(client=self.client, endpoint="tables/platforms/fabric-path/routes", sn=self.sn)

    @property
    def juniper_cluster(self):
        return models.Table(client=self.client, endpoint="tables/platforms/cluster/srx", sn=self.sn)

    @property
    def cisco_fex_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/platforms/fex/interfaces", sn=self.sn)

    @property
    def cisco_fex_modules(self):
        return models.Table(client=self.client, endpoint="tables/platforms/fex/modules", sn=self.sn)

    @property
    def cisco_vdc_devices(self):
        return models.Table(client=self.client, endpoint="tables/platforms/vdc/devices", sn=self.sn)

    @property
    def platform_cisco_vss(self):
        return models.Table(client=self.client, endpoint="tables/platforms/vss/overview", sn=self.sn)

    @property
    def cisco_vss_chassis(self):
        return models.Table(client=self.client, endpoint="tables/platforms/vss/chassis", sn=self.sn)

    @property
    def cisco_vss_vsl(self):
        return models.Table(client=self.client, endpoint="tables/platforms/vss/vsl", sn=self.sn)

    @property
    def poe_devices(self):
        return models.Table(client=self.client, endpoint="tables/platforms/poe/devices", sn=self.sn)

    @property
    def poe_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/platforms/poe/interfaces", sn=self.sn)

    @property
    def poe_modules(self):
        return models.Table(client=self.client, endpoint="tables/platforms/poe/modules", sn=self.sn)

    @property
    def stacks(self):
        return models.Table(client=self.client, endpoint="tables/platforms/stack", sn=self.sn)

    @property
    def stacks_members(self):
        return models.Table(client=self.client, endpoint="tables/platforms/stack/members", sn=self.sn)

    @property
    def stacks_stack_ports(self):
        return models.Table(client=self.client, endpoint="tables/platforms/stack/connections", sn=self.sn)

    @property
    def logical_devices(self):
        return models.Table(client=self.client, endpoint="tables/platforms/devices", sn=self.sn)
