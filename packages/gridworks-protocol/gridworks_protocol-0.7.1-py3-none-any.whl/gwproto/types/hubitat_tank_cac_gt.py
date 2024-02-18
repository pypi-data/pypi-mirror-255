import json
import typing
from typing import Literal

from gwproto.data_classes.cacs.hubitat_tank_module_cac import HubitatTankModuleCac
from gwproto.data_classes.component_attribute_class import ComponentAttributeClass
from gwproto.types.component_attribute_class_gt import ComponentAttributeClassGt


class HubitatTankCacGt(ComponentAttributeClassGt):
    TypeName: Literal["hubitat.tank.cac.gt"] = "hubitat.tank.cac.gt"
    Version: Literal["000"] = "000"

    @classmethod
    def from_data_class(cls, cac: HubitatTankModuleCac) -> "HubitatTankCacGt":
        return HubitatTankCacGt(
            ComponentAttributeClassId=cac.component_attribute_class_id,
            DisplayName=cac.display_name,
        )

    def to_data_class(self) -> HubitatTankModuleCac:
        cac = ComponentAttributeClass.by_id.get(self.ComponentAttributeClassId, None)
        if cac is not None:
            return typing.cast(HubitatTankModuleCac, cac)
        return HubitatTankModuleCac(
            component_attribute_class_id=self.ComponentAttributeClassId,
            display_name=self.DisplayName,
        )

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class HubitatTankCacGt_Maker:
    type_name: str = HubitatTankCacGt.__fields__["TypeName"].default
    version = "000"
    tuple: HubitatTankCacGt

    def __init__(self, cac: HubitatTankModuleCac):
        self.tuple = HubitatTankCacGt.from_data_class(cac)

    @classmethod
    def tuple_to_type(cls, tpl: HubitatTankCacGt) -> str:
        return tpl.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> HubitatTankCacGt:
        return cls.dict_to_tuple(json.loads(t))

    @classmethod
    def dict_to_tuple(cls, d: dict[str, typing.Any]) -> HubitatTankCacGt:
        return HubitatTankCacGt(**d)

    @classmethod
    def tuple_to_dc(cls, t: HubitatTankCacGt) -> HubitatTankModuleCac:
        return t.to_data_class()

    @classmethod
    def dc_to_tuple(cls, dc: HubitatTankModuleCac) -> HubitatTankCacGt:
        return HubitatTankCacGt.from_data_class(dc)

    @classmethod
    def type_to_dc(cls, t: str) -> HubitatTankModuleCac:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: HubitatTankModuleCac) -> str:
        return cls.dc_to_tuple(dc).as_type()

    @classmethod
    def dict_to_dc(cls, d: dict[typing.Any, str]) -> HubitatTankModuleCac:
        return cls.tuple_to_dc(cls.dict_to_tuple(d))
