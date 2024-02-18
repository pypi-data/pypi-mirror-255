import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Security(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def acl(self):
        return models.Table(client=self.client, endpoint="tables/security/acl", sn=self.sn)

    @property
    def acl_interface(self):
        return models.Table(client=self.client, endpoint="tables/security/acl/interfaces", sn=self.sn)

    @property
    def acl_global_policies(self):
        return models.Table(client=self.client, endpoint="tables/security/acl/global-policies", sn=self.sn)

    @property
    def dmvpn(self):
        return models.Table(client=self.client, endpoint="tables/security/dmvpn", sn=self.sn)

    @property
    def dhcp_snooping(self):
        return models.Table(client=self.client, endpoint="tables/security/dhcp/snooping", sn=self.sn)

    @property
    def dhcp_snooping_bindings(self):
        return models.Table(client=self.client, endpoint="tables/security/dhcp/bindings", sn=self.sn)

    @property
    def ipsec_tunnels(self):
        return models.Table(client=self.client, endpoint="tables/security/ipsec/tunnels", sn=self.sn)

    @property
    def ipsec_gateways(self):
        return models.Table(client=self.client, endpoint="tables/security/ipsec/gateways", sn=self.sn)

    @property
    def secure_ports_devices(self):
        return models.Table(client=self.client, endpoint="tables/security/secure-ports/devices", sn=self.sn)

    @property
    def secure_ports_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/security/secure-ports/interfaces", sn=self.sn)

    @property
    def secure_ports_users(self):
        return models.Table(client=self.client, endpoint="tables/security/secure-ports/users", sn=self.sn)

    @property
    def zone_firewall_policies(self):
        return models.Table(client=self.client, endpoint="tables/security/zone-firewall/policies", sn=self.sn)

    @property
    def zone_firewall_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/security/zone-firewall/interfaces", sn=self.sn)
