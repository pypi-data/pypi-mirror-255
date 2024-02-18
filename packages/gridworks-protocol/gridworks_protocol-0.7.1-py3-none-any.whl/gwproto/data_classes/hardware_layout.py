"""(Mostly) static functions describing ShNodes that were in Actor/ActorBase Scada/ScadaBase.

This will probably be refactored as we implement our local registry. Currently separated out here for clarity
because content is static (except for needing a path to the houses.json file, which we should be able to do
away with).
"""
import copy
import json
import re
import typing
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any
from typing import List
from typing import Optional

from gwproto.data_classes.cacs.electric_meter_cac import ElectricMeterCac
from gwproto.data_classes.component import Component
from gwproto.data_classes.component_attribute_class import ComponentAttributeClass
from gwproto.data_classes.components.electric_meter_component import (
    ElectricMeterComponent,
)
from gwproto.data_classes.errors import DataClassLoadingError
from gwproto.data_classes.resolver import ComponentResolver
from gwproto.data_classes.sh_node import ShNode
from gwproto.data_classes.telemetry_tuple import TelemetryTuple
from gwproto.default_decoders import CacDecoder
from gwproto.default_decoders import ComponentDecoder
from gwproto.default_decoders import default_cac_decoder
from gwproto.default_decoders import default_component_decoder
from gwproto.enums import ActorClass
from gwproto.enums import Role
from gwproto.enums import TelemetryName
from gwproto.types import ElectricMeterCacGt_Maker
from gwproto.types import MultipurposeSensorCacGt_Maker
from gwproto.types import PipeFlowSensorCacGt_Maker
from gwproto.types import PipeFlowSensorComponentGt_Maker
from gwproto.types import RelayCacGt_Maker
from gwproto.types import RelayComponentGt_Maker
from gwproto.types import ResistiveHeaterCacGt_Maker
from gwproto.types import ResistiveHeaterComponentGt_Maker
from gwproto.types import SimpleTempSensorCacGt_Maker
from gwproto.types import SimpleTempSensorComponentGt_Maker
from gwproto.types import SpaceheatNodeGt_Maker
from gwproto.types.electric_meter_component_gt import ElectricMeterComponentGt_Maker
from gwproto.types.multipurpose_sensor_component_gt import (
    MultipurposeSensorComponentGt_Maker,
)


snake_add_underscore_to_camel_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def camel_to_snake(name: str) -> str:
    return snake_add_underscore_to_camel_pattern.sub("_", name).lower()


@dataclass
class LoadError:
    type_name: str
    src_dict: dict[Any, Any]
    exception: Exception


def load_cacs(
    layout: dict[str, Any],
    raise_errors: bool = True,
    errors: Optional[list[LoadError]] = None,
    cac_decoder: Optional[CacDecoder] = None,
) -> dict[str, Any]:
    if errors is None:
        errors = []
    cacs = dict()
    for type_name, maker_class in [
        ("RelayCacs", RelayCacGt_Maker),
        ("ResistiveHeaterCacs", ResistiveHeaterCacGt_Maker),
        ("ElectricMeterCacs", ElectricMeterCacGt_Maker),
        ("PipeFlowSensorCacs", PipeFlowSensorCacGt_Maker),
        ("MultipurposeSensorCacs", MultipurposeSensorCacGt_Maker),
        ("SimpleTempSensorCacs", SimpleTempSensorCacGt_Maker),
    ]:
        for d in layout.get(type_name, []):
            try:
                cacs[
                    d["ComponentAttributeClassId"]
                ] = maker_class.dict_to_dc(  # type:ignore[attr-defined]
                    d
                )
            except Exception as e:
                if raise_errors:
                    raise e
                errors.append(LoadError(type_name, d, e))
    if cac_decoder is None:
        cac_decoder = default_cac_decoder
    for d in layout.get("OtherCacs", []):
        cac_type = d.get("TypeName", "")
        try:
            if cac_type and cac_type in cac_decoder:
                cac = cac_decoder.decode_to_data_class(d)
            else:
                cac = ComponentAttributeClass(
                    component_attribute_class_id=d["ComponentAttributeClassId"]
                )
            cacs[d["ComponentAttributeClassId"]] = cac
        except Exception as e:
            if raise_errors:
                raise e
            errors.append(LoadError("OtherCacs", d, e))
    return cacs


def load_components(
    layout: dict[Any, Any],
    raise_errors: bool = True,
    errors: Optional[list[LoadError]] = None,
    component_decoder: Optional[ComponentDecoder] = None,
) -> dict[Any, Any]:
    if errors is None:
        errors = []
    components = dict()
    for type_name, maker_class in [
        ("RelayComponents", RelayComponentGt_Maker),
        ("ResistiveHeaterComponents", ResistiveHeaterComponentGt_Maker),
        ("ElectricMeterComponents", ElectricMeterComponentGt_Maker),
        ("PipeFlowSensorComponents", PipeFlowSensorComponentGt_Maker),
        ("MultipurposeSensorComponents", MultipurposeSensorComponentGt_Maker),
        ("SimpleTempSensorComponents", SimpleTempSensorComponentGt_Maker),
    ]:
        for d in layout.get(type_name, []):
            try:
                components[
                    d["ComponentId"]
                ] = maker_class.dict_to_dc(  # type:ignore[attr-defined]
                    d
                )
            except Exception as e:
                if raise_errors:
                    raise e
                errors.append(LoadError(type_name, d, e))
    if component_decoder is None:
        component_decoder = default_component_decoder
    for d in layout["OtherComponents"]:
        component_type = d.get("TypeName", "")
        try:
            if component_type and component_type in component_decoder:
                component = component_decoder.decode_to_data_class(d)
            else:
                component = Component(**{camel_to_snake(k): v for k, v in d.items()})
            components[d["ComponentId"]] = component
        except Exception as e:
            if raise_errors:
                raise e
            errors.append(LoadError("OtherComponents", d, e))
    return components


def load_nodes(
    layout: dict[Any, Any],
    raise_errors: bool = True,
    errors: Optional[list[LoadError]] = None,
    included_node_names: Optional[set[str]] = None,
) -> dict[Any, Any]:
    nodes = {}
    if errors is None:
        errors = []
    for d in layout.get("ShNodes", []):
        try:
            node_name = d["Alias"]
            if included_node_names is None or node_name in included_node_names:
                nodes[node_name] = SpaceheatNodeGt_Maker.dict_to_dc(d)
        except Exception as e:
            if raise_errors:
                raise e
            errors.append(LoadError("ShNode", d, e))
    return nodes


def resolve_links(
    nodes: dict[str, ShNode],
    components: dict[str, Component],
    raise_errors: bool = True,
    errors: Optional[list[LoadError]] = None,
) -> None:
    if errors is None:
        errors = []
    for node_name, node in nodes.items():
        d = dict(node=dict(name=node_name, node=node))
        try:
            if node.component_id is not None:
                component = components.get(node.component_id, None)
                if component is None:
                    raise DataClassLoadingError(
                        f"{node.alias} component {node.component_id} not loaded!"
                    )
                if isinstance(component, ComponentResolver):
                    component.resolve(
                        node.alias,
                        nodes,
                        components,
                    )
        except Exception as e:
            if raise_errors:
                raise e
            errors.append(LoadError("ShNode", d, e))


class HardwareLayout:
    layout: dict[Any, Any]
    cacs: dict[str, ComponentAttributeClass]
    components: dict[str, Component]
    nodes: dict[str, ShNode]

    def __init__(
        self,
        layout: dict[Any, Any],
        cacs: Optional[dict[str, ComponentAttributeClass]] = None,
        components: Optional[dict[str, Component]] = None,
        nodes: Optional[dict[str, ShNode]] = None,
    ):
        self.layout = copy.deepcopy(layout)
        if cacs is None:
            cacs = ComponentAttributeClass.by_id
        self.cacs = dict(cacs)
        if components is None:
            components = Component.by_id
        self.components = dict(components)
        if nodes is None:
            nodes = ShNode.by_id
        self.nodes = dict(nodes)

    def clear_property_cache(self) -> None:
        for cached_prop_name in [
            prop_name
            for prop_name in type(self).__dict__
            if isinstance(type(self).__dict__[prop_name], cached_property)
        ]:
            self.__dict__.pop(cached_prop_name, None)

    @classmethod
    def load(
        cls,
        layout_path: Path | str,
        included_node_names: Optional[set[str]] = None,
        raise_errors: bool = True,
        errors: Optional[list[LoadError]] = None,
        cac_decoder: Optional[CacDecoder] = None,
        component_decoder: Optional[ComponentDecoder] = None,
    ) -> "HardwareLayout":
        with Path(layout_path).open() as f:
            layout = json.loads(f.read())
        return cls.load_dict(
            layout,
            included_node_names=included_node_names,
            raise_errors=raise_errors,
            errors=errors,
            cac_decoder=cac_decoder,
            component_decoder=component_decoder,
        )

    @classmethod
    def load_dict(
        cls,
        layout: dict[Any, Any],
        included_node_names: Optional[set[str]] = None,
        raise_errors: bool = True,
        errors: Optional[list[LoadError]] = None,
        cac_decoder: Optional[CacDecoder] = None,
        component_decoder: Optional[ComponentDecoder] = None,
    ) -> "HardwareLayout":
        if errors is None:
            errors = []
        load_args = dict(
            cacs=load_cacs(
                layout=layout,
                raise_errors=raise_errors,
                errors=errors,
                cac_decoder=cac_decoder,
            ),
            components=load_components(
                layout=layout,
                raise_errors=raise_errors,
                errors=errors,
                component_decoder=component_decoder,
            ),
            nodes=load_nodes(
                layout=layout,
                raise_errors=raise_errors,
                errors=errors,
                included_node_names=included_node_names,
            ),
        )
        resolve_links(
            load_args["nodes"],
            load_args["components"],
            raise_errors=raise_errors,
            errors=errors,
        )
        return HardwareLayout(layout, **load_args)

    def node(self, alias: str, default: Any = None) -> ShNode:
        return self.nodes.get(alias, default)

    def component(self, alias: str) -> Optional[Component]:
        return self.component_from_node(self.node(alias, None))

    def cac(self, alias: str) -> Optional[ComponentAttributeClass]:
        return self.cac_from_component(self.component(alias))

    def component_from_node(self, node: Optional[ShNode]) -> Optional[Component]:
        return (
            self.components.get(
                node.component_id if node.component_id is not None else "", None
            )
            if node is not None
            else None
        )

    def cac_from_component(
        self, component: Optional[Component]
    ) -> Optional[ComponentAttributeClass]:
        return (
            self.cacs.get(
                component.component_attribute_class_id if component is not None else "",
                None,
            )
            if component is not None
            else None
        )

    @classmethod
    def parent_alias(cls, alias: str) -> str:
        last_delimiter = alias.rfind(".")
        if last_delimiter == -1:
            return ""
        else:
            return alias[:last_delimiter]

    def parent_node(self, alias: str) -> Optional[ShNode]:
        parent_alias = self.parent_alias(alias)
        if not parent_alias:
            return None
        else:
            if parent_alias not in self.nodes:
                raise DataClassLoadingError(
                    f"{alias} is missing parent {parent_alias}!"
                )
            return self.node(parent_alias)

    def descendants(self, alias: str) -> List[ShNode]:
        return list(filter(lambda x: x.alias.startswith(alias), self.nodes.values()))

    @cached_property
    def atn_g_node_alias(self) -> str:
        return self.layout["MyAtomicTNodeGNode"]["Alias"]  # type: ignore[no-any-return]

    @cached_property
    def atn_g_node_instance_id(self) -> str:
        return self.layout["MyAtomicTNodeGNode"]["GNodeId"]  # type: ignore[no-any-return]

    @cached_property
    def atn_g_node_id(self) -> str:
        return self.layout["MyAtomicTNodeGNode"]["GNodeId"]  # type: ignore[no-any-return]

    @cached_property
    def terminal_asset_g_node_alias(self) -> str:
        my_atn_as_dict = self.layout["MyTerminalAssetGNode"]
        return my_atn_as_dict["Alias"]  # type: ignore[no-any-return]

    @cached_property
    def terminal_asset_g_node_id(self) -> str:
        my_atn_as_dict = self.layout["MyTerminalAssetGNode"]
        return my_atn_as_dict["GNodeId"]  # type: ignore[no-any-return]

    @cached_property
    def scada_g_node_alias(self) -> str:
        my_scada_as_dict = self.layout["MyScadaGNode"]
        return my_scada_as_dict["Alias"]  # type: ignore[no-any-return]

    @cached_property
    def scada_g_node_id(self) -> str:
        my_scada_as_dict = self.layout["MyScadaGNode"]
        return my_scada_as_dict["GNodeId"]  # type: ignore[no-any-return]

    @cached_property
    def all_telemetry_tuples_for_agg_power_metering(self) -> List[TelemetryTuple]:
        telemetry_tuples = []
        for node in self.all_nodes_in_agg_power_metering:
            telemetry_tuples += [
                TelemetryTuple(
                    AboutNode=node,
                    SensorNode=self.power_meter_node,
                    TelemetryName=TelemetryName.PowerW,
                )
            ]
        return telemetry_tuples

    @cached_property
    def all_nodes_in_agg_power_metering(self) -> List[ShNode]:
        """All nodes whose power level is metered and included in power reporting by the Scada"""
        all_nodes = list(self.nodes.values())
        return list(filter(lambda x: x.in_power_metering, all_nodes))

    @cached_property
    def all_power_meter_telemetry_tuples(self) -> List[TelemetryTuple]:
        telemetry_tuples = []
        for config in self.power_meter_component.config_list:
            telemetry_tuples.append(
                TelemetryTuple(
                    AboutNode=self.node(config.AboutNodeName),
                    SensorNode=self.power_meter_node,
                    TelemetryName=config.TelemetryName,
                )
            )
        return telemetry_tuples

    @cached_property
    def power_meter_node(self) -> ShNode:
        """Schema for input data enforces exactly one Spaceheat Node with role PowerMeter"""
        power_meter_node = list(
            filter(lambda x: x.role == Role.PowerMeter, self.nodes.values())
        )[0]
        return power_meter_node

    @cached_property
    def power_meter_component(self) -> ElectricMeterComponent:
        if self.power_meter_node.component is None:
            raise ValueError(
                f"ERROR. power_meter_node {self.power_meter_node} has no component."
            )
        c = typing.cast(ElectricMeterComponent, self.power_meter_node.component)
        return c

    @cached_property
    def power_meter_cac(self) -> ElectricMeterCac:
        if not isinstance(
            self.power_meter_component.component_attribute_class, ElectricMeterCac
        ):
            raise ValueError(
                f"ERROR. power_meter_component cac {self.power_meter_component.component_attribute_class}"
                f" / {type(self.power_meter_component.component_attribute_class)} is not an ElectricMeterCac"
            )
        return self.power_meter_node.component.component_attribute_class  # type: ignore[union-attr, return-value]

    @cached_property
    def all_resistive_heaters(self) -> List[ShNode]:
        all_nodes = list(self.nodes.values())
        return list(filter(lambda x: (x.role == Role.BoostElement), all_nodes))

    @cached_property
    def scada_node(self) -> ShNode:
        """Schema for input data enforces exactly one Spaceheat Node with role Scada"""
        nodes = list(filter(lambda x: x.role == Role.Scada, self.nodes.values()))
        return nodes[0]

    @cached_property
    def home_alone_node(self) -> ShNode:
        """Schema for input data enforces exactly one Spaceheat Node with role HomeAlone"""
        nodes = list(filter(lambda x: x.role == Role.HomeAlone, self.nodes.values()))
        return nodes[0]

    @cached_property
    def my_home_alone(self) -> ShNode:
        all_nodes = list(self.nodes.values())
        home_alone_nodes = list(filter(lambda x: (x.role == Role.HomeAlone), all_nodes))
        if len(home_alone_nodes) != 1:
            raise Exception(
                "there should be a single SpaceheatNode with role HomeAlone"
            )
        return home_alone_nodes[0]

    @cached_property
    def my_boolean_actuators(self) -> List[ShNode]:
        all_nodes = list(self.nodes.values())
        return list(filter(lambda x: (x.role == Role.BooleanActuator), all_nodes))

    @cached_property
    def my_simple_sensors(self) -> List[ShNode]:
        all_nodes = list(self.nodes.values())
        return list(
            filter(
                lambda x: (
                    x.actor_class == ActorClass.SimpleSensor
                    or x.actor_class == ActorClass.BooleanActuator
                ),
                all_nodes,
            )
        )

    @cached_property
    def all_multipurpose_telemetry_tuples(self) -> List[TelemetryTuple]:
        multi_nodes = list(
            filter(
                lambda x: (
                    (
                        x.actor_class == ActorClass.MultipurposeSensor
                        or x.actor_class == ActorClass.HubitatTankModule
                        or x.actor_class == ActorClass.HubitatPoller
                    )
                    and hasattr(x.component, "config_list")
                ),
                self.nodes.values(),
            )
        )
        telemetry_tuples = []
        for node in multi_nodes:
            for config in getattr(node.component, "config_list"):
                telemetry_tuples.append(
                    TelemetryTuple(
                        AboutNode=self.node(config.AboutNodeName),
                        SensorNode=node,
                        TelemetryName=config.TelemetryName,
                    )
                )
        return telemetry_tuples

    @cached_property
    def my_multipurpose_sensors(self) -> List[ShNode]:
        """This will be a list of all sensing devices that either measure more
        than one ShNode or measure more than one physical quantity type (or both).
        This includes the (unique) power meter, but may also include other roles like thermostats
        and heat pumps."""
        all_nodes = list(self.nodes.values())
        multi_purpose_roles = [Role.PowerMeter, Role.MultiChannelAnalogTempSensor]
        return list(filter(lambda x: (x.role in multi_purpose_roles), all_nodes))

    @cached_property
    def my_telemetry_tuples(self) -> List[TelemetryTuple]:
        """This will include telemetry tuples from all the multipurpose sensors, the most
        important of which is the power meter."""
        return (
            self.all_power_meter_telemetry_tuples
            + self.all_multipurpose_telemetry_tuples
        )
