import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Interfaces(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def current_rates_data_inbound(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/load/inbound", sn=self.sn)

    @property
    def current_rates_data_outbound(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/load/outbound", sn=self.sn)

    @property
    def current_rates_data_bidirectional(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/load/bidirectional", sn=self.sn)

    @property
    def average_rates_data_inbound(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/transfer-rates/inbound", sn=self.sn)

    @property
    def average_rates_data_outbound(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/transfer-rates/outbound", sn=self.sn)

    @property
    def average_rates_data_bidirectional(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/transfer-rates/bidirectional", sn=self.sn)

    @property
    def average_rates_data_inbound_per_device(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/transfer-rates/inbound-device", sn=self.sn)

    @property
    def average_rates_data_outbound_per_device(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/transfer-rates/outbound-device", sn=self.sn)

    @property
    def average_rates_data_bidirectional_per_device(self):
        return models.Table(
            client=self.client, endpoint="tables/interfaces/transfer-rates/bidirectional-device", sn=self.sn
        )

    @property
    def average_rates_errors_inbound(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/errors/inbound", sn=self.sn)

    @property
    def average_rates_errors_outbound(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/errors/outbound", sn=self.sn)

    @property
    def average_rates_errors_bidirectional(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/errors/bidirectional", sn=self.sn)

    @property
    def average_rates_errors_inbound_per_device(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/errors/inbound-device", sn=self.sn)

    @property
    def average_rates_errors_outbound_per_device(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/errors/outbound-device", sn=self.sn)

    @property
    def average_rates_errors_bidirectional_per_device(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/errors/bidirectional-device", sn=self.sn)

    @property
    def average_rates_drops_inbound(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/drops/inbound", sn=self.sn)

    @property
    def average_rates_drops_outbound(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/drops/outbound", sn=self.sn)

    @property
    def average_rates_drops_bidirectional(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/drops/bidirectional", sn=self.sn)

    @property
    def average_rates_drops_inbound_per_device(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/drops/inbound-device", sn=self.sn)

    @property
    def average_rates_drops_outbound_per_device(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/drops/outbound-device", sn=self.sn)

    @property
    def average_rates_drops_bidirectional_per_device(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/drops/bidirectional-device", sn=self.sn)

    @property
    def duplex(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/duplex", sn=self.sn)

    @property
    def err_disabled(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/errors/disabled", sn=self.sn)

    @property
    def connectivity_matrix(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/connectivity-matrix", sn=self.sn)

    @property
    def connectivity_matrix_unmanaged_neighbors_summary(self):
        return models.Table(
            client=self.client, endpoint="tables/interfaces/connectivity-matrix/unmanaged-neighbors/summary", sn=self.sn
        )

    @property
    def connectivity_matrix_unmanaged_neighbors_detail(self):
        return models.Table(
            client=self.client, endpoint="tables/interfaces/connectivity-matrix/unmanaged-neighbors/detail", sn=self.sn
        )

    @property
    def switchport(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/switchports", sn=self.sn)

    @property
    def mtu(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/mtu", sn=self.sn)

    @property
    def storm_control_all(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/storm-control/all", sn=self.sn)

    @property
    def storm_control_broadcast(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/storm-control/broadcast", sn=self.sn)

    @property
    def storm_control_unicast(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/storm-control/unicast", sn=self.sn)

    @property
    def storm_control_multicast(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/storm-control/multicast", sn=self.sn)

    @property
    def transceivers(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/transceivers/inventory", sn=self.sn)

    @property
    def transceivers_statistics(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/transceivers/statistics", sn=self.sn)

    @property
    def transceivers_triggered_thresholds(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/transceivers/thresholds", sn=self.sn)

    @property
    def transceivers_errors(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/transceivers/errors", sn=self.sn)

    @property
    def point_to_point_over_ethernet(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/pppoe", sn=self.sn)

    @property
    def point_to_point_over_ethernet_sessions(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/pppoe/sessions", sn=self.sn)

    @property
    def counters_inbound(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/counters/inbound", sn=self.sn)

    @property
    def counters_outbound(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/counters/outbound", sn=self.sn)

    @property
    def tunnels_ipv4(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/tunnels/ipv4", sn=self.sn)

    @property
    def tunnels_ipv6(self):
        return models.Table(client=self.client, endpoint="tables/interfaces/tunnels/ipv6", sn=self.sn)
