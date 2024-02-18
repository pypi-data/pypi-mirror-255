from typing import Optional

import yarl

from gwproto.data_classes.component import Component
from gwproto.data_classes.resolver import ComponentResolver
from gwproto.data_classes.sh_node import ShNode
from gwproto.types.hubitat_component_gt import HubitatComponentGt
from gwproto.types.hubitat_poller_gt import HubitatPollerGt
from gwproto.types.rest_poller_gt import RequestArgs
from gwproto.types.rest_poller_gt import RESTPollerSettings
from gwproto.types.telemetry_reporting_config import TelemetryReportingConfig


class HubitatPollerComponent(Component, ComponentResolver):
    hubitat_gt: HubitatComponentGt
    poller_gt: HubitatPollerGt
    _rest: Optional[RESTPollerSettings] = None

    def __init__(
        self,
        component_id: str,
        component_attribute_class_id: str,
        poller_gt: HubitatPollerGt,
        display_name: Optional[str] = None,
        hw_uid: Optional[str] = None,
    ):
        self.hubitat_gt = HubitatComponentGt.make_stub(poller_gt.hubitat_component_id)
        self.poller_gt = poller_gt
        super().__init__(
            component_id=component_id,
            component_attribute_class_id=component_attribute_class_id,
            display_name=display_name,
            hw_uid=hw_uid,
        )

    @property
    def rest(self) -> RESTPollerSettings:
        if self._rest is None:
            raise ValueError(
                f"ERROR. resolve_rest() has not yet been called for {self}."
            )
        return self._rest

    def resolve(
        self,
        tank_node_name: str,
        nodes: dict[str, ShNode],
        components: dict[str, Component],
    ):
        if self._rest is not None:
            raise ValueError(
                f"resolve() must be called exactly once. "
                f"Rest settings already exist for {self}."
            )

        # replace proxy hubitat component, which only had component id.
        # with the actual hubitat component containing data.
        self.hubitat_gt = HubitatComponentGt.from_component_id(
            self.hubitat_gt.ComponentId,
            components,
        )

        # Constuct url config on top of maker api url url config
        self._rest = RESTPollerSettings(
            request=RequestArgs(
                url=self.hubitat_gt.refresh_url_config(self.poller_gt.device_id)
            ),
            poll_period_seconds=self.poller_gt.poll_period_seconds,
        )

    def urls(self) -> dict[str, Optional[yarl.URL]]:
        urls = self.hubitat_gt.urls()
        for attribute in self.poller_gt.attributes:
            urls[attribute.node_name] = self.rest.url
        return urls

    @property
    def config_list(self) -> list[TelemetryReportingConfig]:
        return [
            TelemetryReportingConfig(
                TelemetryName=attribute.telemetry_name,
                AboutNodeName=attribute.node_name,
                ReportOnChange=False,
                SamplePeriodS=int(self.rest.poll_period_seconds),
                Exponent=attribute.exponent,
                Unit=attribute.unit,
            )
            for attribute in self.poller_gt.attributes
        ]
