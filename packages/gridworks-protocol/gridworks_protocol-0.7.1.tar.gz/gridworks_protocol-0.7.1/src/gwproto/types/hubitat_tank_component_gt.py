import copy
import json
import typing
from typing import Any
from typing import Literal

from gwproto.data_classes.component import Component
from gwproto.data_classes.components.hubitat_tank_component import HubitatTankComponent
from gwproto.types.component_gt import ComponentGt
from gwproto.types.hubitat_tank_gt import HubitatTankSettingsGt


class HubitatTankComponentGt(ComponentGt):
    Tank: HubitatTankSettingsGt
    TypeName: Literal["hubitat.tank.component.gt"] = "hubitat.tank.component.gt"
    Version: Literal["000"] = "000"

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))

    @classmethod
    def from_data_class(
        cls, component: HubitatTankComponent
    ) -> "HubitatTankComponentGt":
        return HubitatTankComponentGt(
            ComponentId=component.component_id,
            ComponentAttributeClassId=component.component_attribute_class_id,
            Tank=HubitatTankSettingsGt(
                hubitat_component_id=component.hubitat.ComponentId,
                devices=copy.deepcopy(component.devices),
            ),
            DisplayName=component.display_name,
            HwUid=component.hw_uid,
        )

    def to_data_class(self) -> HubitatTankComponent:
        component = Component.by_id.get(self.ComponentId, None)
        if component is not None:
            return typing.cast(HubitatTankComponent, component)
        return HubitatTankComponent(
            component_id=self.ComponentId,
            component_attribute_class_id=self.ComponentAttributeClassId,
            tank_gt=self.Tank,
            display_name=self.DisplayName,
            hw_uid=self.HwUid,
        )


class HubitatTankComponentGt_Maker:
    type_name: str = HubitatTankComponentGt.__fields__["TypeName"].default
    version = "000"
    tuple: HubitatTankComponentGt

    def __init__(self, component: HubitatTankComponent):
        self.tuple = HubitatTankComponentGt.from_data_class(component)

    @classmethod
    def tuple_to_type(cls, tpl: HubitatTankComponentGt) -> str:
        return tpl.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> HubitatTankComponentGt:
        return cls.dict_to_tuple(json.loads(t))

    @classmethod
    def dict_to_tuple(cls, d: dict[str, Any]) -> HubitatTankComponentGt:
        return HubitatTankComponentGt(**d)

    @classmethod
    def tuple_to_dc(cls, t: HubitatTankComponentGt) -> HubitatTankComponent:
        return t.to_data_class()

    @classmethod
    def dc_to_tuple(cls, dc: HubitatTankComponent) -> HubitatTankComponentGt:
        return HubitatTankComponentGt.from_data_class(dc)

    @classmethod
    def type_to_dc(cls, t: str) -> HubitatTankComponent:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: HubitatTankComponent) -> str:
        return cls.dc_to_tuple(dc).as_type()

    @classmethod
    def dict_to_dc(cls, d: dict[Any, str]) -> HubitatTankComponent:
        return cls.tuple_to_dc(cls.dict_to_tuple(d))
