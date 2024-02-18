"""Type multipurpose.sensor.component.gt, version 000"""
import json
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from gwproto.data_classes.components.multipurpose_sensor_component import (
    MultipurposeSensorComponent,
)
from gwproto.errors import SchemaError
from gwproto.types.telemetry_reporting_config import TelemetryReportingConfig
from gwproto.types.telemetry_reporting_config import TelemetryReportingConfig_Maker


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class MultipurposeSensorComponentGt(BaseModel):
    """
    Type for tracking Multupurpose Sensor Components.

    This type was first designed to work with a 12-channel analog temp sensor built into the
    first generation GridWorks SCADA box (GSCADA 1). It extends the component.gt.000 type. Authority
    for the attributes of the component.gt.000 (ComponentId, ComponentAttributeClassId, DisplayName,
    HwUid) belongs to the WorldRegistry. The WorldRegistry is part of the GridWorks 'BackOffice'
    structure for managing relational device data . Notably, ComponentId and ComponentAttributeClass
    are both required and immutable. HwUid is optional but once it is set to a non-null value
    that is also immutable. The DisplayName is mutable, with its current value in time governed
    by the WorldRegistry.

    [More info](https://gridworks-protocol.readthedocs.io/en/latest/component.html)
    """

    ComponentId: str = Field(
        title="Component Id",
        description=(
            "Primary GridWorks identifier for a specific physical instance of a MultipurposeSensor "
            "(perhaps only the 12-channel analog temp sensor), and also as a more generic Component."
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
    ChannelList: List[int] = Field(
        title="ChannelList",
    )
    ConfigList: List[TelemetryReportingConfig] = Field(
        title="ConfigList",
    )
    HwUid: Optional[str] = Field(
        title="Hardware Unique Id",
        default=None,
    )
    DisplayName: Optional[str] = Field(
        title="DisplayName",
        description="Sample: Oak Multipurpose Temp Sensor Component <100>",
        default=None,
    )
    TypeName: Literal[
        "multipurpose.sensor.component.gt"
    ] = "multipurpose.sensor.component.gt"
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
        multipurpose.sensor.component.gt.000 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        multipurpose.sensor.component.gt.000 type. Unlike the standard python dict method,
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
        # Recursively calling as_dict()
        config_list = []
        for elt in self.ConfigList:
            config_list.append(elt.as_dict())
        d["ConfigList"] = config_list
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the multipurpose.sensor.component.gt.000 representation.

        Instances in the class are python-native representations of multipurpose.sensor.component.gt.000
        objects, while the actual multipurpose.sensor.component.gt.000 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is MultipurposeSensorComponentGt.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class MultipurposeSensorComponentGt_Maker:
    type_name = "multipurpose.sensor.component.gt"
    version = "000"

    def __init__(
        self,
        component_id: str,
        component_attribute_class_id: str,
        channel_list: List[int],
        config_list: List[TelemetryReportingConfig],
        hw_uid: Optional[str],
        display_name: Optional[str],
    ):
        self.tuple = MultipurposeSensorComponentGt(
            ComponentId=component_id,
            ComponentAttributeClassId=component_attribute_class_id,
            ChannelList=channel_list,
            ConfigList=config_list,
            HwUid=hw_uid,
            DisplayName=display_name,
        )

    @classmethod
    def tuple_to_type(cls, tuple: MultipurposeSensorComponentGt) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> MultipurposeSensorComponentGt:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> MultipurposeSensorComponentGt:
        """
        Deserialize a dictionary representation of a multipurpose.sensor.component.gt.000 message object
        into a MultipurposeSensorComponentGt python object for internal use.

        This is the near-inverse of the MultipurposeSensorComponentGt.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a SchemaError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           SchemaError: if the dict cannot be turned into a MultipurposeSensorComponentGt object.

        Returns:
            MultipurposeSensorComponentGt
        """
        d2 = dict(d)
        if "ComponentId" not in d2.keys():
            raise SchemaError(f"dict missing ComponentId: <{d2}>")
        if "ComponentAttributeClassId" not in d2.keys():
            raise SchemaError(f"dict missing ComponentAttributeClass: <{d2}>")
        if "ChannelList" not in d2.keys():
            raise SchemaError(f"dict missing ChannelList: <{d2}>")
        if "ConfigList" not in d2.keys():
            raise SchemaError(f"dict missing ConfigList: <{d2}>")
        if not isinstance(d2["ConfigList"], List):
            raise SchemaError(f"ConfigList <{d2['ConfigList']}> must be a List!")
        config_list = []
        for elt in d2["ConfigList"]:
            if not isinstance(elt, dict):
                raise SchemaError(
                    f"ConfigList <{d2['ConfigList']}> must be a List of TelemetryReportingConfig types"
                )
            t = TelemetryReportingConfig_Maker.dict_to_tuple(elt)
            config_list.append(t)
        d2["ConfigList"] = config_list
        if "TypeName" not in d2.keys():
            raise SchemaError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise SchemaError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "000":
            LOGGER.debug(
                f"Attempting to interpret multipurpose.sensor.component.gt version {d2['Version']} as version 000"
            )
            d2["Version"] = "000"
        return MultipurposeSensorComponentGt(**d2)

    @classmethod
    def tuple_to_dc(
        cls, t: MultipurposeSensorComponentGt
    ) -> MultipurposeSensorComponent:
        if t.ComponentId in MultipurposeSensorComponent.by_id.keys():
            dc = MultipurposeSensorComponent.by_id[t.ComponentId]
        else:
            dc = MultipurposeSensorComponent(
                component_id=t.ComponentId,
                component_attribute_class_id=t.ComponentAttributeClassId,
                channel_list=t.ChannelList,
                config_list=t.ConfigList,
                hw_uid=t.HwUid,
                display_name=t.DisplayName,
            )
        return dc

    @classmethod
    def dc_to_tuple(
        cls, dc: MultipurposeSensorComponent
    ) -> MultipurposeSensorComponentGt:
        t = MultipurposeSensorComponentGt_Maker(
            component_id=dc.component_id,
            component_attribute_class_id=dc.component_attribute_class_id,
            channel_list=dc.channel_list,
            config_list=dc.config_list,
            hw_uid=dc.hw_uid,
            display_name=dc.display_name,
        ).tuple
        return t

    @classmethod
    def type_to_dc(cls, t: str) -> MultipurposeSensorComponent:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: MultipurposeSensorComponent) -> str:
        return cls.dc_to_tuple(dc).as_type()

    @classmethod
    def dict_to_dc(cls, d: dict[Any, str]) -> MultipurposeSensorComponent:
        return cls.tuple_to_dc(cls.dict_to_tuple(d))


def check_is_left_right_dot(v: str) -> None:
    """Checks LeftRightDot Format

    LeftRightDot format: Lowercase alphanumeric words separated by periods, with
    the most significant word (on the left) starting with an alphabet character.

    Args:
        v (str): the candidate

    Raises:
        ValueError: if v is not LeftRightDot format
    """
    from typing import List

    try:
        x: List[str] = v.split(".")
    except:
        raise ValueError(f"Failed to seperate <{v}> into words with split'.'")
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        raise ValueError(
            f"Most significant word of <{v}> must start with alphabet char."
        )
    for word in x:
        if not word.isalnum():
            raise ValueError(f"words of <{v}> split by by '.' must be alphanumeric.")
    if not v.islower():
        raise ValueError(f"All characters of <{v}> must be lowercase.")


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
