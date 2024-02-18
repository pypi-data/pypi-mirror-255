import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Sdn(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def aci_endpoints(self):
        return models.Table(client=self.client, endpoint="tables/aci/endpoints", sn=self.sn)

    @property
    def aci_vlan(self):
        return models.Table(client=self.client, endpoint="tables/aci/vlan", sn=self.sn)

    @property
    def aci_vrf(self):
        return models.Table(client=self.client, endpoint="tables/aci/vrf", sn=self.sn)

    @property
    def aci_dtep(self):
        return models.Table(client=self.client, endpoint="tables/aci/dtep", sn=self.sn)

    @property
    def vxlan_vtep(self):
        return models.Table(client=self.client, endpoint="tables/vxlan/vtep", sn=self.sn)

    @property
    def vxlan_peers(self):
        return models.Table(client=self.client, endpoint="tables/vxlan/peers", sn=self.sn)

    @property
    def vxlan_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/vxlan/interfaces", sn=self.sn)

    @property
    def vxlan_vni(self):
        return models.Table(client=self.client, endpoint="tables/vxlan/vni", sn=self.sn)

    @property
    def apic_controllers(self):
        return models.Table(client=self.client, endpoint="tables/apic/controllers", sn=self.sn)

    @property
    def apic_contexts(self):
        return models.Table(client=self.client, endpoint="tables/apic/contexts", sn=self.sn)

    @property
    def apic_bridge_domains(self):
        return models.Table(client=self.client, endpoint="tables/apic/bridge-domains", sn=self.sn)

    @property
    def apic_applications(self):
        return models.Table(client=self.client, endpoint="tables/apic/applications", sn=self.sn)

    @property
    def apic_endpoint_groups(self):
        return models.Table(client=self.client, endpoint="tables/apic/endpoint-groups", sn=self.sn)

    @property
    def apic_endpoint_groups_contracts(self):
        return models.Table(client=self.client, endpoint="tables/apic/endpoint-groups/contracts", sn=self.sn)

    @property
    def apic_contracts(self):
        return models.Table(client=self.client, endpoint="tables/apic/contracts", sn=self.sn)

    @property
    def apic_service_graphs(self):
        return models.Table(client=self.client, endpoint="tables/apic/service-graphs", sn=self.sn)
