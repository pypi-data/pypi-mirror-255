"""Type multipurpose.sensor.cac.gt, version 000"""
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

from gwproto.data_classes.cacs.multipurpose_sensor_cac import MultipurposeSensorCac
from gwproto.enums import MakeModel as EnumMakeModel
from gwproto.enums import TelemetryName
from gwproto.enums import Unit
from gwproto.errors import SchemaError


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class MultipurposeSensorCacGt(BaseModel):
    """
    Type for tracking Multipuprose Sensor ComponentAttributeClasses.

    GridWorks Spaceheat SCADA uses the GridWorks GNodeRegistry structures and abstractions for
    managing relational device data. The Cac, or ComponentAttributeClass, is part of this structure.

    [More info](https://g-node-registry.readthedocs.io/en/latest/component-attribute-class.html)
    """

    ComponentAttributeClassId: str = Field(
        title="ComponentAttributeClassId",
        description=(
            "Unique identifier for the device class (aka 'cac' or Component Attribute Class). "
            "Authority is maintained by the World Registry."
        ),
    )
    MakeModel: EnumMakeModel = Field(
        title="MakeModel",
        description=(
            "Meant to be enough to articulate any difference in how GridWorks code would interact "
            "with a device. Should be able to use this information to buy or build a device."
        ),
    )
    PollPeriodMs: int = Field(
        title="Poll Period in Milliseconds",
        description=(
            "Poll Period refers to the period of time between two readings by the local actor. "
            "This is in contrast to Capture Period, which refers to the period between readings "
            "that are sent up to the cloud (or otherwise saved for the long-term)."
            "[More info](https://gridworks-protocol.readthedocs.io/en/latest/data-polling-capturing-transmitting.rst)"
        ),
    )
    Exponent: int = Field(
        title="Exponent",
        description=(
            "Say the TelemetryName is WaterTempCTimes1000; this corresponds to units of Celsius. "
            "To match the implication in the name, the Exponent should be 3, and a Value of 65300 "
            "would indicate 65.3 deg C"
        ),
    )
    TempUnit: Unit = Field(
        title="Temp Unit",
    )
    TelemetryNameList: List[TelemetryName] = Field(
        title="TelemetryNameList",
    )
    MaxThermistors: Optional[int] = Field(
        title="MaxThermistors",
        description="The maximum number of temperature sensors this multipurpose sensor can read.",
        default=None,
    )
    DisplayName: Optional[str] = Field(
        title="DisplayName",
        description="Sample: GridWorks TSnap1.0 as 12-channel analog temp sensor",
        default=None,
    )
    CommsMethod: Optional[str] = Field(
        title="CommsMethod",
        default=None,
    )
    TypeName: Literal["multipurpose.sensor.cac.gt"] = "multipurpose.sensor.cac.gt"
    Version: Literal["000"] = "000"

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
        multipurpose.sensor.cac.gt.000 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        multipurpose.sensor.cac.gt.000 type. Unlike the standard python dict method,
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
        del d["MakeModel"]
        d["MakeModelGtEnumSymbol"] = EnumMakeModel.value_to_symbol(self.MakeModel)
        del d["TempUnit"]
        d["TempUnitGtEnumSymbol"] = Unit.value_to_symbol(self.TempUnit)
        del d["TelemetryNameList"]
        telemetry_name_list = []
        for elt in self.TelemetryNameList:
            telemetry_name_list.append(TelemetryName.value_to_symbol(elt.value))
        d["TelemetryNameList"] = telemetry_name_list
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the multipurpose.sensor.cac.gt.000 representation.

        Instances in the class are python-native representations of multipurpose.sensor.cac.gt.000
        objects, while the actual multipurpose.sensor.cac.gt.000 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is MultipurposeSensorCacGt.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class MultipurposeSensorCacGt_Maker:
    type_name = "multipurpose.sensor.cac.gt"
    version = "000"

    def __init__(
        self,
        component_attribute_class_id: str,
        make_model: EnumMakeModel,
        poll_period_ms: int,
        exponent: int,
        temp_unit: Unit,
        telemetry_name_list: List[TelemetryName],
        max_thermistors: Optional[int],
        display_name: Optional[str],
        comms_method: Optional[str],
    ):
        self.tuple = MultipurposeSensorCacGt(
            ComponentAttributeClassId=component_attribute_class_id,
            MakeModel=make_model,
            PollPeriodMs=poll_period_ms,
            Exponent=exponent,
            TempUnit=temp_unit,
            TelemetryNameList=telemetry_name_list,
            MaxThermistors=max_thermistors,
            DisplayName=display_name,
            CommsMethod=comms_method,
        )

    @classmethod
    def tuple_to_type(cls, tuple: MultipurposeSensorCacGt) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> MultipurposeSensorCacGt:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> MultipurposeSensorCacGt:
        """
        Deserialize a dictionary representation of a multipurpose.sensor.cac.gt.000 message object
        into a MultipurposeSensorCacGt python object for internal use.

        This is the near-inverse of the MultipurposeSensorCacGt.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a SchemaError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           SchemaError: if the dict cannot be turned into a MultipurposeSensorCacGt object.

        Returns:
            MultipurposeSensorCacGt
        """
        d2 = dict(d)
        if "ComponentAttributeClassId" not in d2.keys():
            raise SchemaError(f"dict missing ComponentAttributeClassId: <{d2}>")
        if "MakeModelGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"MakeModelGtEnumSymbol missing from dict <{d2}>")
        value = EnumMakeModel.symbol_to_value(d2["MakeModelGtEnumSymbol"])
        d2["MakeModel"] = EnumMakeModel(value)
        if "PollPeriodMs" not in d2.keys():
            raise SchemaError(f"dict missing PollPeriodMs: <{d2}>")
        if "Exponent" not in d2.keys():
            raise SchemaError(f"dict missing Exponent: <{d2}>")
        if "TempUnitGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"TempUnitGtEnumSymbol missing from dict <{d2}>")
        value = Unit.symbol_to_value(d2["TempUnitGtEnumSymbol"])
        d2["TempUnit"] = Unit(value)
        if "TelemetryNameList" not in d2.keys():
            raise SchemaError(f"dict <{d2}> missing TelemetryNameList")
        if not isinstance(d2["TelemetryNameList"], List):
            raise SchemaError("TelemetryNameList must be a List!")
        telemetry_name_list = []
        for elt in d2["TelemetryNameList"]:
            value = TelemetryName.symbol_to_value(elt)
            telemetry_name_list.append(TelemetryName(value))
        d2["TelemetryNameList"] = telemetry_name_list
        if "TypeName" not in d2.keys():
            raise SchemaError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise SchemaError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "000":
            LOGGER.debug(
                f"Attempting to interpret multipurpose.sensor.cac.gt version {d2['Version']} as version 000"
            )
            d2["Version"] = "000"
        return MultipurposeSensorCacGt(**d2)

    @classmethod
    def tuple_to_dc(cls, t: MultipurposeSensorCacGt) -> MultipurposeSensorCac:
        if t.ComponentAttributeClassId in MultipurposeSensorCac.by_id.keys():
            dc = MultipurposeSensorCac.by_id[t.ComponentAttributeClassId]
        else:
            dc = MultipurposeSensorCac(
                component_attribute_class_id=t.ComponentAttributeClassId,
                make_model=t.MakeModel,
                poll_period_ms=t.PollPeriodMs,
                exponent=t.Exponent,
                temp_unit=t.TempUnit,
                telemetry_name_list=t.TelemetryNameList,
                max_thermistors=t.MaxThermistors,
                display_name=t.DisplayName,
                comms_method=t.CommsMethod,
            )
        return dc

    @classmethod
    def dc_to_tuple(cls, dc: MultipurposeSensorCac) -> MultipurposeSensorCacGt:
        t = MultipurposeSensorCacGt_Maker(
            component_attribute_class_id=dc.component_attribute_class_id,
            make_model=dc.make_model,
            poll_period_ms=dc.poll_period_ms,
            exponent=dc.exponent,
            temp_unit=dc.temp_unit,
            telemetry_name_list=dc.telemetry_name_list,
            max_thermistors=dc.max_thermistors,
            display_name=dc.display_name,
            comms_method=dc.comms_method,
        ).tuple
        return t

    @classmethod
    def type_to_dc(cls, t: str) -> MultipurposeSensorCac:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: MultipurposeSensorCac) -> str:
        return cls.dc_to_tuple(dc).as_type()

    @classmethod
    def dict_to_dc(cls, d: dict[Any, str]) -> MultipurposeSensorCac:
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
