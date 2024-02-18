import logging
from typing import Any, Optional

from pydantic import BaseModel

from ipfabric import models

logger = logging.getLogger("ipfabric")


class Management(BaseModel):
    client: Any = None
    sn: Optional[str] = None

    @property
    def aaa_servers(self):
        return models.Table(client=self.client, endpoint="tables/security/aaa/servers", sn=self.sn)

    @property
    def aaa_lines(self):
        return models.Table(client=self.client, endpoint="tables/security/aaa/lines", sn=self.sn)

    @property
    def aaa_authentication(self):
        return models.Table(client=self.client, endpoint="tables/security/aaa/authentication", sn=self.sn)

    @property
    def aaa_authorization(self):
        return models.Table(client=self.client, endpoint="tables/security/aaa/authorization", sn=self.sn)

    @property
    def aaa_accounting(self):
        return models.Table(client=self.client, endpoint="tables/security/aaa/accounting", sn=self.sn)

    @property
    def aaa_users(self):
        return models.Table(client=self.client, endpoint="tables/security/aaa/users", sn=self.sn)

    @property
    def aaa_password_strength(self):
        return models.Table(client=self.client, endpoint="tables/security/aaa/password-strength", sn=self.sn)

    @property
    def telnet_access(self):
        return models.Table(client=self.client, endpoint="tables/security/enabled-telnet", sn=self.sn)

    @property
    def saved_config_consistency(self):
        return models.Table(client=self.client, endpoint="tables/management/configuration/saved", sn=self.sn)

    @property
    def ntp_summary(self):
        return models.Table(client=self.client, endpoint="tables/management/ntp/summary", sn=self.sn)

    @property
    def ntp_sources(self):
        return models.Table(client=self.client, endpoint="tables/management/ntp/sources", sn=self.sn)

    @property
    def port_mirroring(self):
        return models.Table(client=self.client, endpoint="tables/management/port-mirroring", sn=self.sn)

    @property
    def logging_summary(self):
        return models.Table(client=self.client, endpoint="tables/management/logging/summary", sn=self.sn)

    @property
    def logging_remote(self):
        return models.Table(client=self.client, endpoint="tables/management/logging/remote", sn=self.sn)

    @property
    def logging_local(self):
        return models.Table(client=self.client, endpoint="tables/management/logging/local", sn=self.sn)

    @property
    def flow_overview(self):
        return models.Table(client=self.client, endpoint="tables/management/flow/overview", sn=self.sn)

    @property
    def netflow_devices(self):
        return models.Table(client=self.client, endpoint="tables/management/flow/netflow/devices", sn=self.sn)

    @property
    def netflow_collectors(self):
        return models.Table(client=self.client, endpoint="tables/management/flow/netflow/collectors", sn=self.sn)

    @property
    def netflow_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/management/flow/netflow/interfaces", sn=self.sn)

    @property
    def sflow_devices(self):
        return models.Table(client=self.client, endpoint="tables/management/flow/sflow/devices", sn=self.sn)

    @property
    def sflow_collectors(self):
        return models.Table(client=self.client, endpoint="tables/management/flow/sflow/collectors", sn=self.sn)

    @property
    def sflow_sources(self):
        return models.Table(client=self.client, endpoint="tables/management/flow/sflow/sources", sn=self.sn)

    @property
    def snmp_summary(self):
        return models.Table(client=self.client, endpoint="tables/management/snmp/summary", sn=self.sn)

    @property
    def snmp_communities(self):
        return models.Table(client=self.client, endpoint="tables/management/snmp/communities", sn=self.sn)

    @property
    def snmp_trap_hosts(self):
        return models.Table(client=self.client, endpoint="tables/management/snmp/trap-hosts", sn=self.sn)

    @property
    def snmp_users(self):
        return models.Table(client=self.client, endpoint="tables/management/snmp/users", sn=self.sn)

    @property
    def ptp_local_clock(self):
        return models.Table(client=self.client, endpoint="tables/management/ptp/local-clock", sn=self.sn)

    @property
    def ptp_masters(self):
        return models.Table(client=self.client, endpoint="tables/management/ptp/masters", sn=self.sn)

    @property
    def ptp_interfaces(self):
        return models.Table(client=self.client, endpoint="tables/management/ptp/interfaces", sn=self.sn)

    @property
    def license_summary(self):
        return models.Table(client=self.client, endpoint="tables/management/licenses/summary", sn=self.sn)

    @property
    def licenses(self):
        return models.Table(client=self.client, endpoint="tables/management/licenses", sn=self.sn)

    @property
    def licenses_detail(self):
        return models.Table(client=self.client, endpoint="tables/management/licenses/detail", sn=self.sn)

    @property
    def cisco_smart_licenses_authorization(self):
        return models.Table(
            client=self.client, endpoint="tables/management/licenses/cisco-smart-licenses/authorization", sn=self.sn
        )

    @property
    def cisco_smart_licenses_registration(self):
        return models.Table(
            client=self.client, endpoint="tables/management/licenses/cisco-smart-licenses/registration", sn=self.sn
        )

    @property
    def cisco_smart_licenses_reservations(self):
        return models.Table(
            client=self.client, endpoint="tables/management/licenses/cisco-smart-licenses/reservations", sn=self.sn
        )

    @property
    def dns_resolver_settings(self):
        return models.Table(client=self.client, endpoint="tables/management/dns/settings", sn=self.sn)

    @property
    def dns_resolver_servers(self):
        return models.Table(client=self.client, endpoint="tables/management/dns/servers", sn=self.sn)

    @property
    def banners_summary(self):
        return models.Table(client=self.client, endpoint="tables/management/banners/summary", sn=self.sn)

    @property
    def banners_detail(self):
        return models.Table(client=self.client, endpoint="tables/management/banners/banners", sn=self.sn)
