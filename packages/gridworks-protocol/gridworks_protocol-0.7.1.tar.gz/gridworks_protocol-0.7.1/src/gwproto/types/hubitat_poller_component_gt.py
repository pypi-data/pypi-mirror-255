import copy
import typing
from typing import Literal

from gwproto.data_classes.component import Component
from gwproto.data_classes.components.hubitat_poller_component import (
    HubitatPollerComponent,
)
from gwproto.types.component_gt import ComponentGt
from gwproto.types.hubitat_poller_gt import HubitatPollerGt


class HubitatPollerComponentGt(ComponentGt):
    Poller: HubitatPollerGt
    TypeName: Literal["hubitat.poller.component.gt"] = "hubitat.poller.component.gt"
    Version: Literal["000"] = "000"

    @classmethod
    def from_data_class(
        cls, component: HubitatPollerComponent
    ) -> "HubitatPollerComponentGt":
        return HubitatPollerComponentGt(
            ComponentId=component.component_id,
            ComponentAttributeClassId=component.component_attribute_class_id,
            Poller=copy.deepcopy(component.poller_gt),
            DisplayName=component.display_name,
            HwUid=component.hw_uid,
        )

    def to_data_class(self) -> HubitatPollerComponent:
        component = Component.by_id.get(self.ComponentId, None)
        if component is not None:
            return typing.cast(HubitatPollerComponent, component)
        return HubitatPollerComponent(
            component_id=self.ComponentId,
            component_attribute_class_id=self.ComponentAttributeClassId,
            poller_gt=copy.deepcopy(self.Poller),
            display_name=self.DisplayName,
            hw_uid=self.HwUid,
        )


class HubitatPollerComponentGt_Maker:
    type_name = "hubitat.poller.component.gt"
    version = "000"
