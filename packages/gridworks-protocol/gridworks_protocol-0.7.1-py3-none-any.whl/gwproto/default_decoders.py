import re
import typing
from typing import Type
from typing import TypeVar

import gwproto.types.fibaro_smart_implant_cac_gt  # noqa
import gwproto.types.fibaro_smart_implant_component_gt  # noqa
import gwproto.types.hubitat_cac_gt  # noqa
import gwproto.types.hubitat_component_gt  # noqa
import gwproto.types.hubitat_poller_cac_gt  # noqa
import gwproto.types.hubitat_poller_component_gt  # noqa
import gwproto.types.hubitat_tank_cac_gt  # noqa
import gwproto.types.hubitat_tank_component_gt  # noqa
import gwproto.types.rest_poller_cac_gt  # noqa
import gwproto.types.rest_poller_component_gt  # noqa
from gwproto.data_classes.component import Component
from gwproto.data_classes.component_attribute_class import ComponentAttributeClass
from gwproto.decoders import PydanticTypeNameDecoder


T = TypeVar("T")


def decode_to_data_class(
    decoded_gt: typing.Any,
    return_type: Type[T],
    allow_missing_func: bool = True,
    allow_non_instance: bool = False,
) -> T:
    if hasattr(decoded_gt, "to_data_class"):
        data_class = decoded_gt.to_data_class()
        if not allow_non_instance and not isinstance(data_class, return_type):
            raise ValueError(
                f"ERROR. Returned data class {type(data_class)} is not"
                f" instance of {return_type}"
            )
        return typing.cast(T, decoded_gt.to_data_class())
    if allow_missing_func:
        raise ValueError(
            f"ERROR. Decoded type {type(decoded_gt)} has no" f" to_data_class() method."
        )
    return Component(**decoded_gt.dict())


class CacDecoder(PydanticTypeNameDecoder):
    TYPE_NAME_REGEX = re.compile(r".*\.cac\.gt")

    def __init__(self, model_name: str, **kwargs):
        if "type_name_regex" not in kwargs:
            kwargs["type_name_regex"] = CacDecoder.TYPE_NAME_REGEX
        super().__init__(model_name, **kwargs)

    def decode_to_data_class(
        self, data: dict, allow_missing_func: bool = True
    ) -> ComponentAttributeClass:
        return decode_to_data_class(
            decoded_gt=self.decode_obj(data),
            return_type=ComponentAttributeClass,
            allow_missing_func=allow_missing_func,
        )


class ComponentDecoder(PydanticTypeNameDecoder):
    TYPE_NAME_REGEX = re.compile(r".*\.component\.gt")

    def __init__(self, model_name: str, **kwargs):
        if "type_name_regex" not in kwargs:
            kwargs["type_name_regex"] = ComponentDecoder.TYPE_NAME_REGEX
        super().__init__(model_name, **kwargs)

    def decode_to_data_class(
        self, data: dict, allow_missing_func: bool = True
    ) -> Component:
        return decode_to_data_class(
            decoded_gt=self.decode_obj(data),
            return_type=Component,
            allow_missing_func=allow_missing_func,
        )


default_cac_decoder = CacDecoder(
    model_name="DefaultCacDecoder",
    module_names=[
        "gwproto.types.fibaro_smart_implant_cac_gt",
        "gwproto.types.hubitat_cac_gt",
        "gwproto.types.hubitat_poller_cac_gt",
        "gwproto.types.hubitat_tank_cac_gt",
        "gwproto.types.rest_poller_cac_gt",
    ],
)

default_component_decoder = ComponentDecoder(
    model_name="DefaultComponentDecoder",
    module_names=[
        "gwproto.types.fibaro_smart_implant_component_gt",
        "gwproto.types.hubitat_component_gt",
        "gwproto.types.hubitat_poller_component_gt",
        "gwproto.types.hubitat_tank_component_gt",
        "gwproto.types.rest_poller_component_gt",
    ],
)
