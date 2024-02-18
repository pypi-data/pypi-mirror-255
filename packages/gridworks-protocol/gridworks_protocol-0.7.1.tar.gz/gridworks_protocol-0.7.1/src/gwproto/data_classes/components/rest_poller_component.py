from typing import Optional

from gwproto.data_classes.component import Component
from gwproto.types.rest_poller_gt import RESTPollerSettings


class RESTPollerComponent(Component):
    rest: RESTPollerSettings

    def __init__(
        self,
        component_id: str,
        component_attribute_class_id: str,
        rest: RESTPollerSettings,
        display_name: Optional[str] = None,
        hw_uid: Optional[str] = None,
    ):
        self.rest = rest
        super().__init__(
            display_name=display_name,
            component_id=component_id,
            hw_uid=hw_uid,
            component_attribute_class_id=component_attribute_class_id,
        )
