from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models
from .addressing import Addressing
from .cloud import Cloud
from .dhcp import Dhcp
from .fhrp import Fhrp
from .interfaces import Interfaces
from .ip_telephony import IpTelephony
from .load_balancing import LoadBalancing
from .managed_networks import ManagedNetworks
from .management import Management
from .mpls import Mpls
from .multicast import Multicast
from .neighbors import Neighbors
from .oam import Oam
from .platforms import Platforms
from .port_channels import PortChannels
from .qos import Qos
from .routing import Routing
from .sdn import Sdn
from .sdwan import Sdwan
from .security import Security
from .stp import Stp
from .vlans import Vlans
from .wireless import Wireless


class Technology(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def platforms(self):
        return Platforms(client=self.client, sn=self.sn)

    @property
    def interfaces(self):
        return Interfaces(client=self.client, sn=self.sn)

    @property
    def neighbors(self):
        return Neighbors(client=self.client, sn=self.sn)

    @property
    def dhcp(self):
        return Dhcp(client=self.client, sn=self.sn)

    @property
    def port_channels(self):
        return PortChannels(client=self.client, sn=self.sn)

    @property
    def vlans(self):
        return Vlans(client=self.client, sn=self.sn)

    @property
    def stp(self):
        return Stp(client=self.client, sn=self.sn)

    @property
    def addressing(self):
        return Addressing(client=self.client, sn=self.sn)

    @property
    def fhrp(self):
        return Fhrp(client=self.client, sn=self.sn)

    @property
    def managed_networks(self):
        return ManagedNetworks(client=self.client, sn=self.sn)

    @property
    def mpls(self):
        return Mpls(client=self.client, sn=self.sn)

    @property
    def multicast(self):
        return Multicast(client=self.client, sn=self.sn)

    @property
    def cloud(self):
        return Cloud(client=self.client, sn=self.sn)

    @property
    def management(self):
        return Management(client=self.client, sn=self.sn)

    @property
    def ip_telephony(self):
        return IpTelephony(client=self.client, sn=self.sn)

    @property
    def load_balancing(self):
        return LoadBalancing(client=self.client, sn=self.sn)

    @property
    def oam(self):
        return Oam(client=self.client, sn=self.sn)

    @property
    def qos(self):
        return Qos(client=self.client, sn=self.sn)

    @property
    def routing(self):
        return Routing(client=self.client, sn=self.sn)

    @property
    def sdn(self):
        return Sdn(client=self.client, sn=self.sn)

    @property
    def sdwan(self):
        return Sdwan(client=self.client, sn=self.sn)

    @property
    def security(self):
        return Security(client=self.client, sn=self.sn)

    @property
    def wireless(self):
        return Wireless(client=self.client, sn=self.sn)

    @property
    def serial_ports(self):
        return models.Table(client=self.client, endpoint="tables/serial-ports", sn=self.sn)


__all__ = ["Technology"]
