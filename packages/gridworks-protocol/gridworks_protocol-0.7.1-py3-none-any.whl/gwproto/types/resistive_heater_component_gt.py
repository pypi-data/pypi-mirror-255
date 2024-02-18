"""Type resistive.heater.component.gt, version 000"""
import json
import logging
from typing import Any
from typing import Dict
from typing import Literal
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from gwproto.data_classes.components.resistive_heater_component import (
    ResistiveHeaterComponent,
)
from gwproto.errors import SchemaError


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class ResistiveHeaterComponentGt(BaseModel):
    """
    Type for tracking Resistive Heater Components.

    Designed for Resistive Heaters. It extends the component.gt.000 type. Authority for the
    attributes of the component.gt.000 (ComponentId, ComponentAttributeClassId, DisplayName,
    HwUid) belongs to the WorldRegistry. The WorldRegistry is part of the GridWorks 'BackOffice'
    structure for managing relational device data . Notably, ComponentId and ComponentAttributeClass
    are both required and immutable. HwUid is optional but once it is set to a non-null value
    that is also immutable - it is meant to be an immutable identifier associated to a specific
    physical device, ideally one that can be read remotely by the SCADA and also by the naked
    eye. The DisplayName is mutable, with its current value in time governed by the WorldRegistry.

    [More info](https://g-node-registry.readthedocs.io/en/latest/component.html)
    """

    ComponentId: str = Field(
        title="Component Id",
        description=(
            "Primary GridWorks identifier for a specific physical instance of a ResistiveHeater, "
            "and also as a more generic Component."
        ),
    )
    ComponentAttributeClassId: str = Field(
        title="ComponentAttributeClassId",
        description=(
            "Unique identifier for the device class. Authority for these, as well as the relationship "
            "between Components and ComponentAttributeClasses (Cacs) is maintained by the World "
            "Registry."
        ),
    )
    DisplayName: Optional[str] = Field(
        title="DisplayName",
        default=None,
    )
    HwUid: Optional[str] = Field(
        title="Hardware Unique Id",
        default=None,
    )
    TestedMaxHotMilliOhms: Optional[int] = Field(
        title="TestedMaxHotMilliOhms",
        default=None,
    )
    TestedMaxColdMilliOhms: Optional[int] = Field(
        title="TestedMaxColdMilliOhms",
        default=None,
    )
    TypeName: Literal["resistive.heater.component.gt"] = "resistive.heater.component.gt"
    Version: Literal["000"] = "000"

    @validator("ComponentId")
    def _check_component_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"ComponentId failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    @validator("ComponentAttributeClassId")
    def _check_component_attribute_class_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"ComponentAttributeClassId failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        """
        Translate the object into a dictionary representation that can be serialized into a
        resistive.heater.component.gt.000 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        resistive.heater.component.gt.000 type. Unlike the standard python dict method,
        it makes the following substantive changes:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.
        """
        d = {
            key: value
            for key, value in self.dict(
                include=self.__fields_set__ | {"TypeName", "Version"}
            ).items()
            if value is not None
        }
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the resistive.heater.component.gt.000 representation.

        Instances in the class are python-native representations of resistive.heater.component.gt.000
        objects, while the actual resistive.heater.component.gt.000 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is ResistiveHeaterComponentGt.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class ResistiveHeaterComponentGt_Maker:
    type_name = "resistive.heater.component.gt"
    version = "000"

    def __init__(
        self,
        component_id: str,
        component_attribute_class_id: str,
        display_name: Optional[str],
        hw_uid: Optional[str],
        tested_max_hot_milli_ohms: Optional[int],
        tested_max_cold_milli_ohms: Optional[int],
    ):
        self.tuple = ResistiveHeaterComponentGt(
            ComponentId=component_id,
            ComponentAttributeClassId=component_attribute_class_id,
            DisplayName=display_name,
            HwUid=hw_uid,
            TestedMaxHotMilliOhms=tested_max_hot_milli_ohms,
            TestedMaxColdMilliOhms=tested_max_cold_milli_ohms,
        )

    @classmethod
    def tuple_to_type(cls, tuple: ResistiveHeaterComponentGt) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> ResistiveHeaterComponentGt:
        """
        Given a serialized JSON type object, returns the Python class object.
        """
        try:
            d = json.loads(t)
        except TypeError:
            raise SchemaError("Type must be string or bytes!")
        if not isinstance(d, dict):
            raise SchemaError(f"Deserializing <{t}> must result in dict!")
        return cls.dict_to_tuple(d)

    @classmethod
    def dict_to_tuple(cls, d: dict[str, Any]) -> ResistiveHeaterComponentGt:
        """
        Deserialize a dictionary representation of a resistive.heater.component.gt.000 message object
        into a ResistiveHeaterComponentGt python object for internal use.

        This is the near-inverse of the ResistiveHeaterComponentGt.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a SchemaError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           SchemaError: if the dict cannot be turned into a ResistiveHeaterComponentGt object.

        Returns:
            ResistiveHeaterComponentGt
        """
        d2 = dict(d)
        if "ComponentId" not in d2.keys():
            raise SchemaError(f"dict missing ComponentId: <{d2}>")
        if "ComponentAttributeClassId" not in d2.keys():
            raise SchemaError(f"dict missing ComponentAttributeClass: <{d2}>")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise SchemaError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "000":
            LOGGER.debug(
                f"Attempting to interpret resistive.heater.component.gt version {d2['Version']} as version 000"
            )
            d2["Version"] = "000"
        return ResistiveHeaterComponentGt(**d2)

    @classmethod
    def tuple_to_dc(cls, t: ResistiveHeaterComponentGt) -> ResistiveHeaterComponent:
        if t.ComponentId in ResistiveHeaterComponent.by_id.keys():
            dc = ResistiveHeaterComponent.by_id[t.ComponentId]
        else:
            dc = ResistiveHeaterComponent(
                component_id=t.ComponentId,
                component_attribute_class_id=t.ComponentAttributeClassId,
                display_name=t.DisplayName,
                hw_uid=t.HwUid,
                tested_max_hot_milli_ohms=t.TestedMaxHotMilliOhms,
                tested_max_cold_milli_ohms=t.TestedMaxColdMilliOhms,
            )
        return dc

    @classmethod
    def dc_to_tuple(cls, dc: ResistiveHeaterComponent) -> ResistiveHeaterComponentGt:
        t = ResistiveHeaterComponentGt_Maker(
            component_id=dc.component_id,
            component_attribute_class_id=dc.component_attribute_class_id,
            display_name=dc.display_name,
            hw_uid=dc.hw_uid,
            tested_max_hot_milli_ohms=dc.tested_max_hot_milli_ohms,
            tested_max_cold_milli_ohms=dc.tested_max_cold_milli_ohms,
        ).tuple
        return t

    @classmethod
    def type_to_dc(cls, t: str) -> ResistiveHeaterComponent:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: ResistiveHeaterComponent) -> str:
        return cls.dc_to_tuple(dc).as_type()

    @classmethod
    def dict_to_dc(cls, d: dict[Any, str]) -> ResistiveHeaterComponent:
        return cls.tuple_to_dc(cls.dict_to_tuple(d))


def check_is_uuid_canonical_textual(v: str) -> None:
    """Checks UuidCanonicalTextual format

    UuidCanonicalTextual format:  A string of hex words separated by hyphens
    of length 8-4-4-4-12.

    Args:
        v (str): the candidate

    Raises:
        ValueError: if v is not UuidCanonicalTextual format
    """
    try:
        x = v.split("-")
    except AttributeError as e:
        raise ValueError(f"Failed to split on -: {e}")
    if len(x) != 5:
        raise ValueError(f"<{v}> split by '-' did not have 5 words")
    for hex_word in x:
        try:
            int(hex_word, 16)
        except ValueError:
            raise ValueError(f"Words of <{v}> are not all hex")
    if len(x[0]) != 8:
        raise ValueError(f"<{v}> word lengths not 8-4-4-4-12")
    if len(x[1]) != 4:
        raise ValueError(f"<{v}> word lengths not 8-4-4-4-12")
    if len(x[2]) != 4:
        raise ValueError(f"<{v}> word lengths not 8-4-4-4-12")
    if len(x[3]) != 4:
        raise ValueError(f"<{v}> word lengths not 8-4-4-4-12")
    if len(x[4]) != 12:
        raise ValueError(f"<{v}> word lengths not 8-4-4-4-12")
