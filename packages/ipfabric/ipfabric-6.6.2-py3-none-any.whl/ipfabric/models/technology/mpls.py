import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Mpls(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def ldp_neighbors(self):
        return models.Table(client=self.client, endpoint="tables/mpls/ldp/neighbors", sn=self.sn)

    @property
    def ldp_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/mpls/ldp/interfaces", sn=self.sn)

    @property
    def rsvp_neighbors(self):
        return models.Table(client=self.client, endpoint="tables/mpls/rsvp/neighbors", sn=self.sn)

    @property
    def rsvp_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/mpls/rsvp/interfaces", sn=self.sn)

    @property
    def forwarding(self):
        return models.Table(client=self.client, endpoint="tables/mpls/forwarding", sn=self.sn)

    @property
    def l3vpn_pe_routers(self):
        return models.Table(client=self.client, endpoint="tables/mpls/l3-vpn/pe-routers", sn=self.sn)

    @property
    def l3vpn_pe_vrfs(self):
        return models.Table(client=self.client, endpoint="tables/mpls/l3-vpn/pe-vrfs", sn=self.sn)

    @property
    def l3vpn_vrf_targets(self):
        return models.Table(client=self.client, endpoint="tables/mpls/l3-vpn/vrf-targets", sn=self.sn)

    @property
    def l3vpn_pe_routes(self):
        return models.Table(client=self.client, endpoint="tables/mpls/l3-vpn/pe-routes", sn=self.sn)

    @property
    def l2vpn_point_to_point_vpws(self):
        return models.Table(client=self.client, endpoint="tables/mpls/l2-vpn/point-to-point-vpws", sn=self.sn)

    @property
    def l2vpn_point_to_multipoint(self):
        return models.Table(client=self.client, endpoint="tables/mpls/l2-vpn/point-to-multipoint", sn=self.sn)

    @property
    def l2vpn_circuit_cross_connect(self):
        return models.Table(client=self.client, endpoint="tables/mpls/l2-vpn/circuit-cross-connect", sn=self.sn)

    @property
    def l2vpn_pseudowires(self):
        return models.Table(client=self.client, endpoint="tables/mpls/l2-vpn/pseudowires", sn=self.sn)
