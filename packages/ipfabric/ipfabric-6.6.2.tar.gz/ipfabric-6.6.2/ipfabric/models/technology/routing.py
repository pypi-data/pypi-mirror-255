import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Routing(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def summary_protocols(self):
        return models.Table(client=self.client, endpoint="tables/networks/summary/protocols", sn=self.sn)

    @property
    def summary_protocols_bgp(self):
        return models.Table(client=self.client, endpoint="tables/networks/summary/protocols/bgp", sn=self.sn)

    @property
    def summary_protocols_eigrp(self):
        return models.Table(client=self.client, endpoint="tables/networks/summary/protocols/eigrp", sn=self.sn)

    @property
    def summary_protocols_isis(self):
        return models.Table(client=self.client, endpoint="tables/networks/summary/protocols/isis", sn=self.sn)

    @property
    def summary_protocols_ospf(self):
        return models.Table(client=self.client, endpoint="tables/networks/summary/protocols/ospf", sn=self.sn)

    @property
    def summary_protocols_ospfv3(self):
        return models.Table(client=self.client, endpoint="tables/networks/summary/protocols/ospfv3", sn=self.sn)

    @property
    def summary_protocols_rip(self):
        return models.Table(client=self.client, endpoint="tables/networks/summary/protocols/rip", sn=self.sn)

    @property
    def routes_ipv4(self):
        return models.Table(client=self.client, endpoint="tables/networks/routes", sn=self.sn)

    @property
    def routes_ipv6(self):
        return models.Table(client=self.client, endpoint="tables/networks/ipv6-routes", sn=self.sn)

    @property
    def route_stability(self):
        return models.Table(client=self.client, endpoint="tables/networks/route-stability", sn=self.sn)

    @property
    def ospf_neighbors(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/ospf/neighbors", sn=self.sn)

    @property
    def ospf_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/ospf/interfaces", sn=self.sn)

    @property
    def ospfv3_neighbors(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/ospf-v3/neighbors", sn=self.sn)

    @property
    def ospfv3_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/ospf-v3/interfaces", sn=self.sn)

    @property
    def bgp_neighbors(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/bgp/neighbors", sn=self.sn)

    @property
    def bgp_address_families(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/bgp/address-families", sn=self.sn)

    @property
    def eigrp_neighbors(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/eigrp/neighbors", sn=self.sn)

    @property
    def eigrp_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/eigrp/interfaces", sn=self.sn)

    @property
    def rip_neighbors(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/rip/neighbors", sn=self.sn)

    @property
    def rip_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/rip/interfaces", sn=self.sn)

    @property
    def isis_neighbors(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/is-is/neighbors", sn=self.sn)

    @property
    def isis_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/is-is/interfaces", sn=self.sn)

    @property
    def isis_levels(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/is-is/levels", sn=self.sn)

    @property
    def path_lookup_checks(self):
        return models.Table(client=self.client, endpoint="tables/networks/path-lookup-checks", sn=self.sn)

    @property
    def vrf_summary(self):
        return models.Table(client=self.client, endpoint="tables/vrf/summary", sn=self.sn)

    @property
    def vrf_detail(self):
        return models.Table(client=self.client, endpoint="tables/vrf/detail", sn=self.sn)

    @property
    def vrf_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/vrf/interfaces", sn=self.sn)

    @property
    def policies_prefix_list(self):
        return models.Table(client=self.client, endpoint="tables/networks/policies/prefix-lists/ipv4", sn=self.sn)

    @property
    def policies_prefix_list_ipv6(self):
        return models.Table(client=self.client, endpoint="tables/networks/policies/prefix-lists/ipv6", sn=self.sn)

    @property
    def lisp_routes_ipv4(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/lisp/ipv4-routes", sn=self.sn)

    @property
    def lisp_routes_ipv6(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/lisp/ipv6-routes", sn=self.sn)

    @property
    def lisp_map_resolvers_ipv4(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/lisp/ipv4-databases", sn=self.sn)

    @property
    def lisp_map_resolvers_ipv6(self):
        return models.Table(client=self.client, endpoint="tables/routing/protocols/lisp/ipv6-databases", sn=self.sn)

    @property
    def policies(self):
        return models.Table(client=self.client, endpoint="tables/networks/policies/routing", sn=self.sn)

    @property
    def policies_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/networks/policies/routing/interfaces", sn=self.sn)

    @property
    def policies_pbr(self):
        return models.Table(client=self.client, endpoint="tables/security/pbr", sn=self.sn)
