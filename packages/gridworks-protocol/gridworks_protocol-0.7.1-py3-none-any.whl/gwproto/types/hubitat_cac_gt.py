import json
import typing
from typing import Literal

from gwproto.data_classes.cacs.hubitat_cac import HubitatCac
from gwproto.data_classes.component_attribute_class import ComponentAttributeClass
from gwproto.types.component_attribute_class_gt import ComponentAttributeClassGt


class HubitatCacGt(ComponentAttributeClassGt):
    TypeName: Literal["hubitat.cac.gt"] = "hubitat.cac.gt"
    Version: Literal["000"] = "000"

    @classmethod
    def from_data_class(cls, cac: HubitatCac) -> "HubitatCacGt":
        return HubitatCacGt(
            ComponentAttributeClassId=cac.component_attribute_class_id,
            DisplayName=cac.display_name,
        )

    def to_data_class(self) -> HubitatCac:
        cac = ComponentAttributeClass.by_id.get(self.ComponentAttributeClassId, None)
        if cac is not None:
            return typing.cast(HubitatCac, cac)
        return HubitatCac(
            component_attribute_class_id=self.ComponentAttributeClassId,
            display_name=self.DisplayName,
        )

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class HubitatCacGt_Maker:
    type_name: str = HubitatCacGt.__fields__["TypeName"].default
    version = "000"
    tuple: HubitatCacGt

    def __init__(self, cac: HubitatCac):
        self.tuple = HubitatCacGt.from_data_class(cac)

    @classmethod
    def tuple_to_type(cls, tpl: HubitatCacGt) -> str:
        return tpl.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> HubitatCacGt:
        return cls.dict_to_tuple(json.loads(t))

    @classmethod
    def dict_to_tuple(cls, d: dict[str, typing.Any]) -> HubitatCacGt:
        return HubitatCacGt(**d)

    @classmethod
    def tuple_to_dc(cls, t: HubitatCacGt) -> HubitatCac:
        return t.to_data_class()

    @classmethod
    def dc_to_tuple(cls, dc: HubitatCac) -> HubitatCacGt:
        return HubitatCacGt.from_data_class(dc)

    @classmethod
    def type_to_dc(cls, t: str) -> HubitatCac:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: HubitatCac) -> str:
        return cls.dc_to_tuple(dc).as_type()

    @classmethod
    def dict_to_dc(cls, d: dict[typing.Any, str]) -> HubitatCac:
        return cls.tuple_to_dc(cls.dict_to_tuple(d))
