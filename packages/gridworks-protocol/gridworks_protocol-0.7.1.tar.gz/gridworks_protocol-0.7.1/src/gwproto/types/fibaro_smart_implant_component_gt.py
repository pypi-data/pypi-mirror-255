import json
import typing
from typing import Any
from typing import Literal

from gwproto.data_classes.component import Component
from gwproto.data_classes.components.fibaro_smart_implant_component import (
    FibaroSmartImplantComponent,
)
from gwproto.types import ComponentGt


class FibaroSmartImplantComponentGt(ComponentGt):
    ZWaveDSK: str = ""
    TypeName: Literal[
        "fibaro.smart.implant.component.gt"
    ] = "fibaro.smart.implant.component.gt"
    Version: Literal["000"] = "000"

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))

    @classmethod
    def from_data_class(
        cls, component: FibaroSmartImplantComponent
    ) -> "FibaroSmartImplantComponentGt":
        return FibaroSmartImplantComponentGt(
            ComponentId=component.component_id,
            ComponentAttributeClassId=component.component_attribute_class_id,
            DisplayName=component.display_name,
            HwUid=component.hw_uid,
        )

    def to_data_class(self) -> FibaroSmartImplantComponent:
        component = Component.by_id.get(self.ComponentId, None)
        if component is not None:
            return typing.cast(FibaroSmartImplantComponent, component)
        return FibaroSmartImplantComponent(
            component_id=self.ComponentId,
            component_attribute_class_id=self.ComponentAttributeClassId,
            display_name=self.DisplayName,
            hw_uid=self.HwUid,
        )


class FibaroSmartImplantComponentGt_Maker:
    type_name: str = FibaroSmartImplantComponentGt.__fields__["TypeName"].default
    version = "000"
    tuple: FibaroSmartImplantComponentGt

    def __init__(self, component: FibaroSmartImplantComponent):
        self.tuple = FibaroSmartImplantComponentGt.from_data_class(component)

    @classmethod
    def tuple_to_type(cls, tpl: FibaroSmartImplantComponentGt) -> str:
        return tpl.as_type()

    @classmethod
    def type_to_tuple(cls, t: str) -> FibaroSmartImplantComponentGt:
        return cls.dict_to_tuple(json.loads(t))

    @classmethod
    def dict_to_tuple(cls, d: dict[str, Any]) -> FibaroSmartImplantComponentGt:
        return FibaroSmartImplantComponentGt(**d)

    @classmethod
    def tuple_to_dc(
        cls, t: FibaroSmartImplantComponentGt
    ) -> FibaroSmartImplantComponent:
        return t.to_data_class()

    @classmethod
    def dc_to_tuple(
        cls, dc: FibaroSmartImplantComponent
    ) -> FibaroSmartImplantComponentGt:
        return FibaroSmartImplantComponentGt.from_data_class(dc)

    @classmethod
    def type_to_dc(cls, t: str) -> FibaroSmartImplantComponent:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: FibaroSmartImplantComponent) -> str:
        return cls.dc_to_tuple(dc).as_type()

    @classmethod
    def dict_to_dc(cls, d: dict[Any, str]) -> FibaroSmartImplantComponent:
        return cls.tuple_to_dc(cls.dict_to_tuple(d))
