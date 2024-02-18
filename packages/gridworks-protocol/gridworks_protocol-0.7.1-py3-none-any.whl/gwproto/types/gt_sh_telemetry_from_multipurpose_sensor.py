"""Type gt.sh.telemetry.from.multipurpose.sensor, version 100"""
import json
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Literal

from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from gwproto.enums import TelemetryName
from gwproto.errors import SchemaError


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class GtShTelemetryFromMultipurposeSensor(BaseModel):
    """
    Data sent from a MultipurposeSensor to a Spaceheat SCADA.

    A set of readings made at the same time by a multipurpose sensor, sent by the MultipurposeSensor
    SpaceheatNode actor to its SCADA. The nth element of each of its three readings (what is
    getting read, what the value is, what the TelemetryNames are).

    [More info](https://gridworks-protocol.readthedocs.io/en/latest/multipurpose-sensor.html)
    """

    ScadaReadTimeUnixMs: int = Field(
        title="ScadaReadTime in Unix MilliSeconds",
    )
    AboutNodeAliasList: List[str] = Field(
        title="AboutNodeAliasList",
        description="List of aliases of the SpaceHeat Nodes getting measured",
    )
    TelemetryNameList: List[TelemetryName] = Field(
        title="TelemetryNameList",
        description=(
            "List of the TelemetryNames. The nth name in this list indicates the TelemetryName "
            "of the nth alias in the AboutNodeAliasList."
            "[More info](https://gridworks-protocol.readthedocs.io/en/latest/enums.html#gridworks-protocol.enums.TelemetryName)"
        ),
    )
    ValueList: List[int] = Field(
        title="ValueList",
    )
    TypeName: Literal[
        "gt.sh.telemetry.from.multipurpose.sensor"
    ] = "gt.sh.telemetry.from.multipurpose.sensor"
    Version: Literal["100"] = "100"

    @validator("ScadaReadTimeUnixMs")
    def _check_scada_read_time_unix_ms(cls, v: int) -> int:
        try:
            check_is_reasonable_unix_time_ms(v)
        except ValueError as e:
            raise ValueError(
                f"ScadaReadTimeUnixMs failed ReasonableUnixTimeMs format validation: {e}"
            )
        return v

    @validator("AboutNodeAliasList")
    def _check_about_node_alias_list(cls, v: List[str]) -> List[str]:
        for elt in v:
            try:
                check_is_left_right_dot(elt)
            except ValueError as e:
                raise ValueError(
                    f"AboutNodeAliasList element {elt} failed LeftRightDot format validation: {e}"
                )
        return v

    @root_validator
    def check_axiom_1(cls, v: dict) -> dict:
        """
        Axiom 1: ListLengthConsistency.
        AboutNodeAliasList, ValueList and TelemetryNameList must all have the same length.
        """
        alias_list: List[str] = v.get("AboutNodeAliasList", None)
        value_list: List[int] = v.get("ValueList", None)
        tn_list: List[TelemetryName] = v.get("TelemetryNameList", None)
        if (len(value_list) != len(alias_list)) or (len(value_list) != len(tn_list)):
            raise ValueError(
                "Axiom 1: AboutNodeAliasList, ValueList and TelemetryNameList must all have the same length."
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        """
        Translate the object into a dictionary representation that can be serialized into a
        gt.sh.telemetry.from.multipurpose.sensor.100 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        gt.sh.telemetry.from.multipurpose.sensor.100 type. Unlike the standard python dict method,
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
        del d["TelemetryNameList"]
        telemetry_name_list = []
        for elt in self.TelemetryNameList:
            telemetry_name_list.append(TelemetryName.value_to_symbol(elt.value))
        d["TelemetryNameList"] = telemetry_name_list
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the gt.sh.telemetry.from.multipurpose.sensor.100 representation.

        Instances in the class are python-native representations of gt.sh.telemetry.from.multipurpose.sensor.100
        objects, while the actual gt.sh.telemetry.from.multipurpose.sensor.100 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is GtShTelemetryFromMultipurposeSensor.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class GtShTelemetryFromMultipurposeSensor_Maker:
    type_name = "gt.sh.telemetry.from.multipurpose.sensor"
    version = "100"

    def __init__(
        self,
        scada_read_time_unix_ms: int,
        about_node_alias_list: List[str],
        telemetry_name_list: List[TelemetryName],
        value_list: List[int],
    ):
        self.tuple = GtShTelemetryFromMultipurposeSensor(
            ScadaReadTimeUnixMs=scada_read_time_unix_ms,
            AboutNodeAliasList=about_node_alias_list,
            TelemetryNameList=telemetry_name_list,
            ValueList=value_list,
        )

    @classmethod
    def tuple_to_type(cls, tuple: GtShTelemetryFromMultipurposeSensor) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> GtShTelemetryFromMultipurposeSensor:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> GtShTelemetryFromMultipurposeSensor:
        """
        Deserialize a dictionary representation of a gt.sh.telemetry.from.multipurpose.sensor.100 message object
        into a GtShTelemetryFromMultipurposeSensor python object for internal use.

        This is the near-inverse of the GtShTelemetryFromMultipurposeSensor.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a SchemaError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           SchemaError: if the dict cannot be turned into a GtShTelemetryFromMultipurposeSensor object.

        Returns:
            GtShTelemetryFromMultipurposeSensor
        """
        d2 = dict(d)
        if "ScadaReadTimeUnixMs" not in d2.keys():
            raise SchemaError(f"dict missing ScadaReadTimeUnixMs: <{d2}>")
        if "AboutNodeAliasList" not in d2.keys():
            raise SchemaError(f"dict missing AboutNodeAliasList: <{d2}>")
        if "TelemetryNameList" not in d2.keys():
            raise SchemaError(f"dict <{d2}> missing TelemetryNameList")
        if not isinstance(d2["TelemetryNameList"], List):
            raise SchemaError("TelemetryNameList must be a List!")
        telemetry_name_list = []
        for elt in d2["TelemetryNameList"]:
            value = TelemetryName.symbol_to_value(elt)
            telemetry_name_list.append(TelemetryName(value))
        d2["TelemetryNameList"] = telemetry_name_list
        if "ValueList" not in d2.keys():
            raise SchemaError(f"dict missing ValueList: <{d2}>")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise SchemaError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "100":
            LOGGER.debug(
                f"Attempting to interpret gt.sh.telemetry.from.multipurpose.sensor version {d2['Version']} as version 100"
            )
            d2["Version"] = "100"
        return GtShTelemetryFromMultipurposeSensor(**d2)


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


def check_is_reasonable_unix_time_ms(v: int) -> None:
    """Checks ReasonableUnixTimeMs format

    ReasonableUnixTimeMs format: unix milliseconds between Jan 1 2000 and Jan 1 3000

    Args:
        v (int): the candidate

    Raises:
        ValueError: if v is not ReasonableUnixTimeMs format
    """
    import pendulum

    if pendulum.parse("2000-01-01T00:00:00Z").int_timestamp * 1000 > v:  # type: ignore[attr-defined]
        raise ValueError(f"<{v}> must be after Jan 1 2000")
    if pendulum.parse("3000-01-01T00:00:00Z").int_timestamp * 1000 < v:  # type: ignore[attr-defined]
        raise ValueError(f"<{v}> must be before Jan 1 3000")
