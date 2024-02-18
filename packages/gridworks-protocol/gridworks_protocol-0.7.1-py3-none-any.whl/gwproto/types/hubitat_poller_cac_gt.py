import json
import typing
from typing import Literal

from gwproto.data_classes.cacs.hubitat_cac import HubitatCac
from gwproto.data_classes.cacs.hubitat_poller_cac import HubitatPollerCac
from gwproto.data_classes.component_attribute_class import ComponentAttributeClass
from gwproto.types.component_attribute_class_gt import ComponentAttributeClassGt


class HubitatPollerCacGt(ComponentAttributeClassGt):
    TypeName: Literal["hubitat.poller.cac.gt"] = "hubitat.poller.cac.gt"
    Version: Literal["000"] = "000"

    @classmethod
    def from_data_class(cls, cac: HubitatCac) -> "HubitatPollerCacGt":
        return HubitatPollerCacGt(
            ComponentAttributeClassId=cac.component_attribute_class_id,
            DisplayName=cac.display_name,
        )

    def to_data_class(self) -> HubitatPollerCac:
        cac = ComponentAttributeClass.by_id.get(self.ComponentAttributeClassId, None)
        if cac is not None:
            return typing.cast(HubitatPollerCac, cac)
        return HubitatPollerCac(
            component_attribute_class_id=self.ComponentAttributeClassId,
            display_name=self.DisplayName,
        )

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class HubitatPollerCacGt_Maker:
    type_name = "hubitat.poller.cac.gt"
    version = "000"
