import json
import typing
from typing import Any
from typing import Literal

from gwproto.data_classes.cacs.rest_poller_cac import RESTPollerCac
from gwproto.data_classes.component_attribute_class import ComponentAttributeClass
from gwproto.types import ComponentAttributeClassGt


class RESTPollerCacGt(ComponentAttributeClassGt):
    TypeName: Literal["rest.poller.cac.gt"] = "rest.poller.cac.gt"
    Version: Literal["000"] = "000"

    @classmethod
    def from_data_class(cls, cac: RESTPollerCac) -> "RESTPollerCacGt":
        return RESTPollerCacGt(
            ComponentAttributeClassId=cac.component_attribute_class_id,
            DisplayName=cac.display_name,
        )

    def to_data_class(self) -> RESTPollerCac:
        cac = ComponentAttributeClass.by_id.get(self.ComponentAttributeClassId, None)
        if cac is not None:
            return typing.cast(RESTPollerCac, cac)
        return RESTPollerCac(
            component_attribute_class_id=self.ComponentAttributeClassId,
            display_name=self.DisplayName,
        )

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class RESTPollerCacGt_Maker:
    type_name: str = RESTPollerCacGt.__fields__["TypeName"].default
    version = "000"
    tuple: RESTPollerCacGt

    def __init__(self, cac: RESTPollerCac):
        self.tuple = RESTPollerCacGt.from_data_class(cac)

    @classmethod
    def tuple_to_type(cls, tpl: RESTPollerCacGt) -> str:
        return tpl.as_type()  # noqa

    @classmethod
    def type_to_tuple(cls, t: str) -> RESTPollerCacGt:
        return cls.dict_to_tuple(json.loads(t))

    @classmethod
    def dict_to_tuple(cls, d: dict[str, Any]) -> RESTPollerCacGt:
        return RESTPollerCacGt(**d)

    @classmethod
    def tuple_to_dc(cls, t: RESTPollerCacGt) -> RESTPollerCac:
        return t.to_data_class()

    @classmethod
    def dc_to_tuple(cls, dc: RESTPollerCac) -> RESTPollerCacGt:
        return RESTPollerCacGt.from_data_class(dc)

    @classmethod
    def type_to_dc(cls, t: str) -> RESTPollerCac:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: RESTPollerCac) -> str:
        return cls.dc_to_tuple(dc).as_type()  # noqa

    @classmethod
    def dict_to_dc(cls, d: dict[Any, str]) -> RESTPollerCac:
        return cls.tuple_to_dc(cls.dict_to_tuple(d))
