from typing import Optional

import yarl

from gwproto.data_classes.component import Component
from gwproto.types.hubitat_gt import HubitatGt


class HubitatComponent(Component):
    hubitat_gt: HubitatGt

    def __init__(
        self,
        component_id: str,
        component_attribute_class_id: str,
        hubitat_gt: HubitatGt,
        display_name: Optional[str] = None,
        hw_uid: Optional[str] = None,
    ):
        self.hubitat_gt = hubitat_gt
        super().__init__(
            component_id=component_id,
            component_attribute_class_id=component_attribute_class_id,
            display_name=display_name,
            hw_uid=hw_uid,
        )

    def urls(self) -> dict[str, Optional[yarl.URL]]:
        return self.hubitat_gt.urls()
