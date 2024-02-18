from typing import Any
from typing import Callable
from typing import Generic
from typing import Mapping
from typing import Optional
from typing import TypeVar
from typing import Union

from pydantic import BaseModel
from pydantic import Field
from pydantic.generics import GenericModel

from gwproto.topic import MQTTTopic


EnumType = TypeVar("EnumType")


def as_enum(
    value: Any, enum_type: Callable[[Any], EnumType], default: Optional[EnumType] = None
) -> Optional[EnumType]:
    try:
        return enum_type(value)
    except ValueError:
        return default


class Header(BaseModel):
    Src: str
    Dst: str = ""
    MessageType: str
    MessageId: str = ""
    AckRequired: bool = False
    TypeName: str = Field("gridworks.header", const=True)


PayloadT = TypeVar("PayloadT")

PAYLOAD_TYPE_FIELDS = ["TypeName", "type_alias", "TypeName", "type_name"]

GRIDWORKS_ENVELOPE_TYPE = "gw"


def ensure_arg(arg_name: str, default_value: Any, kwargs_dict: dict) -> None:
    if arg_name not in kwargs_dict:
        payload = kwargs_dict.get("Payload", None)
        if payload is None or not hasattr(payload, arg_name):
            kwargs_dict[arg_name] = default_value


class Message(GenericModel, Generic[PayloadT]):
    Header: Header
    Payload: PayloadT
    TypeName: str = Field(GRIDWORKS_ENVELOPE_TYPE, const=True)

    def __init__(self, **kwargs: Any):
        kwargs["Header"] = self._header_from_kwargs(kwargs)
        super().__init__(**kwargs)

    def message_type(self) -> str:
        return self.Header.MessageType

    def src(self) -> str:
        return self.Header.Src

    @classmethod
    def type_name(cls) -> str:
        return Message.__fields__["TypeName"].default

    def mqtt_topic(self) -> str:
        return MQTTTopic.encode(self.type_name(), self.src(), self.message_type())

    @classmethod
    def _header_from_kwargs(cls, kwargs: dict[str, Any]) -> Header:
        header_kwargs = dict()
        if "Payload" in kwargs:
            payload = kwargs["Payload"]
            for header_field, payload_fields in [
                ("Src", ["Src"]),
                ("Dst", ["Dst"]),
                ("MessageId", ["MessageId"]),
                ("MessageType", PAYLOAD_TYPE_FIELDS),
                ("AckRequired", ["AckRequired"]),
            ]:
                val = kwargs.get(header_field, None)
                if val is None:
                    for payload_field in payload_fields:
                        if hasattr(payload, payload_field):
                            val = getattr(payload, payload_field)
                        elif isinstance(payload, Mapping) and payload_field in payload:
                            val = payload[payload_field]
                if val is not None:
                    header_kwargs[header_field] = val
        header: Optional[Union[Header, dict[str, Any]]] = kwargs.get("Header", None)
        if isinstance(header, Header):
            header = header.copy(update=header_kwargs, deep=True)
        else:
            if header is not None:
                header_kwargs = dict(header, **header_kwargs)
            header = Header(**header_kwargs)
        return header
