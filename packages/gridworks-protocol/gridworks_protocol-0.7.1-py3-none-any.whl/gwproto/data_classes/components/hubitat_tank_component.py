from typing import Optional

import yarl

from gwproto.data_classes.component import Component
from gwproto.data_classes.resolver import ComponentResolver
from gwproto.data_classes.sh_node import ShNode
from gwproto.types.hubitat_component_gt import HubitatComponentGt
from gwproto.types.hubitat_component_gt import HubitatRESTResolutionSettings
from gwproto.types.hubitat_tank_gt import FibaroTempSensorSettings
from gwproto.types.hubitat_tank_gt import FibaroTempSensorSettingsGt
from gwproto.types.hubitat_tank_gt import HubitatTankSettingsGt
from gwproto.types.telemetry_reporting_config import TelemetryReportingConfig


class HubitatTankComponent(Component, ComponentResolver):
    hubitat: HubitatComponentGt
    sensor_supply_voltage: float
    default_poll_period_seconds: Optional[float] = None
    devices_gt: list[FibaroTempSensorSettingsGt]
    devices: list[FibaroTempSensorSettings] = []

    def __init__(
        self,
        component_id: str,
        component_attribute_class_id: str,
        tank_gt: HubitatTankSettingsGt,
        display_name: Optional[str] = None,
        hw_uid: Optional[str] = None,
    ):
        # Create self.hubitat as a proxy containing only the id
        # of the hubitat; the actual component data will be resolved
        # when resolve() is called; Here in the constructor we cannot
        # rely on the actual HubitatComponentGt existing yet.
        self.hubitat = HubitatComponentGt.make_stub(tank_gt.hubitat_component_id)
        self.sensor_supply_voltage = tank_gt.sensor_supply_voltage
        self.default_poll_period_seconds = tank_gt.default_poll_period_seconds
        self.devices_gt = list(tank_gt.devices)
        super().__init__(
            display_name=display_name,
            component_id=component_id,
            hw_uid=hw_uid,
            component_attribute_class_id=component_attribute_class_id,
        )

    def resolve(
        self,
        tank_node_name: str,
        nodes: dict[str, ShNode],
        components: dict[str, Component],
    ):
        hubitat_component_gt = HubitatComponentGt.from_component_id(
            self.hubitat.ComponentId, components
        )
        hubitat_settings = HubitatRESTResolutionSettings(hubitat_component_gt)
        devices = [
            FibaroTempSensorSettings.create(
                tank_name=tank_node_name,
                settings_gt=device_gt,
                hubitat=hubitat_settings,
                default_poll_period_seconds=self.default_poll_period_seconds,
            )
            for device_gt in self.devices_gt
            if device_gt.enabled
        ]
        for device in devices:
            if device.node_name not in nodes:
                raise ValueError(
                    f"ERROR. Node not found for tank temp sensor <{device.node_name}>"
                )
        # replace proxy hubitat component, which only had component id.
        # with the actual hubitat component containing data.
        self.hubitat = hubitat_component_gt
        self.devices = devices

    def urls(self) -> dict[str, Optional[yarl.URL]]:
        urls = self.hubitat.urls()
        for device in self.devices:
            urls[device.node_name] = device.url
        return urls

    @property
    def config_list(self) -> list[TelemetryReportingConfig]:
        return [
            TelemetryReportingConfig(
                TelemetryName=device.telemetry_name,
                AboutNodeName=device.node_name,
                ReportOnChange=False,
                SamplePeriodS=int(device.rest.poll_period_seconds),
                Exponent=device.exponent,
                Unit=device.unit,
            )
            for device in self.devices
        ]
