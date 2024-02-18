"""Type pipe.flow.sensor.component.gt, version 000"""
import json
import logging
from typing import Any
from typing import Dict
from typing import Literal
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from gwproto.data_classes.components.pipe_flow_sensor_component import (
    PipeFlowSensorComponent,
)
from gwproto.errors import SchemaError


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class PipeFlowSensorComponentGt(BaseModel):
    """
    Type for tracking Pipe Flow Sensor Components.

    Designed for Pipe Flow Sensors. It extends the component.gt.000 type. Authority for the
    attributes of the component.gt.000 (ComponentId, ComponentAttributeClassId, DisplayName,
    HwUid) belongs to the WorldRegistry. The WorldRegistry is part of the GridWorks 'BackOffice'
    structure for managing relational device data . Notably, ComponentId and ComponentAttributeClass
    are both required and immutable. HwUid is optional but once it is set to a non-null value
    that is also immutable - it is meant to be an immutable identifier associated to a specific
    physical device, ideally one that can be read remotely by the SCADA and also by the naked
    eye. The DisplayName is mutable, with its current value in time governed by the WorldRegistry.

    [More info](https://gridworks-protocol.readthedocs.io/en/latest/component.html)
    """

    ComponentId: str = Field(
        title="Component Id",
        description=(
            "Primary GridWorks identifier for a specific physical instance of a PipeFlowSensor, "
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
    I2cAddress: int = Field(
        title="I2cAddress",
    )
    ConversionFactor: float = Field(
        title="ConversionFactor",
    )
    DisplayName: Optional[str] = Field(
        title="DisplayName",
        description="Sample: Pipe Flow Meter Component <dist-flow>",
        default=None,
    )
    HwUid: Optional[str] = Field(
        title="Hardware Unique Id",
        default=None,
    )
    ExpectedMaxGpmTimes100: Optional[int] = Field(
        title="Expected Max Flow in Gallons per Minute, times 100",
        default=None,
    )
    TypeName: Literal["pipe.flow.sensor.component.gt"] = "pipe.flow.sensor.component.gt"
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
        pipe.flow.sensor.component.gt.000 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        pipe.flow.sensor.component.gt.000 type. Unlike the standard python dict method,
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
        Serialize to the pipe.flow.sensor.component.gt.000 representation.

        Instances in the class are python-native representations of pipe.flow.sensor.component.gt.000
        objects, while the actual pipe.flow.sensor.component.gt.000 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is PipeFlowSensorComponentGt.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class PipeFlowSensorComponentGt_Maker:
    type_name = "pipe.flow.sensor.component.gt"
    version = "000"

    def __init__(
        self,
        component_id: str,
        component_attribute_class_id: str,
        i2c_address: int,
        conversion_factor: float,
        display_name: Optional[str],
        hw_uid: Optional[str],
        expected_max_gpm_times100: Optional[int],
    ):
        self.tuple = PipeFlowSensorComponentGt(
            ComponentId=component_id,
            ComponentAttributeClassId=component_attribute_class_id,
            I2cAddress=i2c_address,
            ConversionFactor=conversion_factor,
            DisplayName=display_name,
            HwUid=hw_uid,
            ExpectedMaxGpmTimes100=expected_max_gpm_times100,
        )

    @classmethod
    def tuple_to_type(cls, tuple: PipeFlowSensorComponentGt) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> PipeFlowSensorComponentGt:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> PipeFlowSensorComponentGt:
        """
        Deserialize a dictionary representation of a pipe.flow.sensor.component.gt.000 message object
        into a PipeFlowSensorComponentGt python object for internal use.

        This is the near-inverse of the PipeFlowSensorComponentGt.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a SchemaError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           SchemaError: if the dict cannot be turned into a PipeFlowSensorComponentGt object.

        Returns:
            PipeFlowSensorComponentGt
        """
        d2 = dict(d)
        if "ComponentId" not in d2.keys():
            raise SchemaError(f"dict missing ComponentId: <{d2}>")
        if "ComponentAttributeClassId" not in d2.keys():
            raise SchemaError(f"dict missing ComponentAttributeClass: <{d2}>")
        if "I2cAddress" not in d2.keys():
            raise SchemaError(f"dict missing I2cAddress: <{d2}>")
        if "ConversionFactor" not in d2.keys():
            raise SchemaError(f"dict missing ConversionFactor: <{d2}>")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise SchemaError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "000":
            LOGGER.debug(
                f"Attempting to interpret pipe.flow.sensor.component.gt version {d2['Version']} as version 000"
            )
            d2["Version"] = "000"
        return PipeFlowSensorComponentGt(**d2)

    @classmethod
    def tuple_to_dc(cls, t: PipeFlowSensorComponentGt) -> PipeFlowSensorComponent:
        if t.ComponentId in PipeFlowSensorComponent.by_id.keys():
            dc = PipeFlowSensorComponent.by_id[t.ComponentId]
        else:
            dc = PipeFlowSensorComponent(
                component_id=t.ComponentId,
                component_attribute_class_id=t.ComponentAttributeClassId,
                i2c_address=t.I2cAddress,
                conversion_factor=t.ConversionFactor,
                display_name=t.DisplayName,
                hw_uid=t.HwUid,
                expected_max_gpm_times100=t.ExpectedMaxGpmTimes100,
            )
        return dc

    @classmethod
    def dc_to_tuple(cls, dc: PipeFlowSensorComponent) -> PipeFlowSensorComponentGt:
        t = PipeFlowSensorComponentGt_Maker(
            component_id=dc.component_id,
            component_attribute_class_id=dc.component_attribute_class_id,
            i2c_address=dc.i2c_address,
            conversion_factor=dc.conversion_factor,
            display_name=dc.display_name,
            hw_uid=dc.hw_uid,
            expected_max_gpm_times100=dc.expected_max_gpm_times100,
        ).tuple
        return t

    @classmethod
    def type_to_dc(cls, t: str) -> PipeFlowSensorComponent:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: PipeFlowSensorComponent) -> str:
        return cls.dc_to_tuple(dc).as_type()

    @classmethod
    def dict_to_dc(cls, d: dict[Any, str]) -> PipeFlowSensorComponent:
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
