"""Type telemetry.reporting.config, version 000"""
import json
import logging
from typing import Any
from typing import Dict
from typing import Literal
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from gwproto.enums import TelemetryName as EnumTelemetryName
from gwproto.enums import Unit as EnumUnit
from gwproto.errors import SchemaError


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class TelemetryReportingConfig(BaseModel):
    """ """

    TelemetryName: EnumTelemetryName = Field(
        title="TelemetryName",
    )
    AboutNodeName: str = Field(
        title="AboutNodeName",
        description="The name of the SpaceheatNode whose physical quantity is getting captured.",
    )
    ReportOnChange: bool = Field(
        title="ReportOnChange",
    )
    SamplePeriodS: int = Field(
        title="SamplePeriodS",
    )
    Exponent: int = Field(
        title="Exponent",
        description=(
            "Say the TelemetryName is WaterTempCTimes1000; this corresponds to units of Celsius. "
            "To match the implication in the name, the Exponent should be 3, and a Value of 65300 "
            "would indicate 65.3 deg C"
        ),
    )
    Unit: EnumUnit = Field(
        title="Unit",
    )
    AsyncReportThreshold: Optional[float] = Field(
        title="AsyncReportThreshold",
        default=None,
    )
    NameplateMaxValue: Optional[int] = Field(
        title="NameplateMaxValue",
        default=None,
    )
    TypeName: Literal["telemetry.reporting.config"] = "telemetry.reporting.config"
    Version: Literal["000"] = "000"

    @validator("AboutNodeName")
    def _check_about_node_name(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(
                f"AboutNodeName failed LeftRightDot format validation: {e}"
            )
        return v

    @validator("NameplateMaxValue")
    def _check_nameplate_max_value(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        try:
            check_is_positive_integer(v)
        except ValueError as e:
            raise ValueError(
                f"NameplateMaxValue failed PositiveInteger format validation: {e}"
            )
        return v

    @root_validator
    def check_axiom_1(cls, v: dict) -> dict:
        """
        Axiom 1: Async reporting consistency.
        If AsyncReportThreshold exists, so does NameplateMaxValue
        """
        AsyncReportThreshold = v.get("AsyncReportThreshold", None)
        NameplateMaxValue = v.get("NameplateMaxValue", None)
        if AsyncReportThreshold is not None:
            if NameplateMaxValue is None:
                raise ValueError(
                    f"Violates Axiom 1: If AsyncReportThreshold exists, so does NameplateMaxValue"
                )
        return v

    def as_dict(self) -> Dict[str, Any]:
        """
        Translate the object into a dictionary representation that can be serialized into a
        telemetry.reporting.config.000 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        telemetry.reporting.config.000 type. Unlike the standard python dict method,
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
        del d["TelemetryName"]
        d["TelemetryNameGtEnumSymbol"] = EnumTelemetryName.value_to_symbol(
            self.TelemetryName
        )
        del d["Unit"]
        d["UnitGtEnumSymbol"] = EnumUnit.value_to_symbol(self.Unit)
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the telemetry.reporting.config.000 representation.

        Instances in the class are python-native representations of telemetry.reporting.config.000
        objects, while the actual telemetry.reporting.config.000 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is TelemetryReportingConfig.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class TelemetryReportingConfig_Maker:
    type_name = "telemetry.reporting.config"
    version = "000"

    def __init__(
        self,
        telemetry_name: EnumTelemetryName,
        about_node_name: str,
        report_on_change: bool,
        sample_period_s: int,
        exponent: int,
        unit: EnumUnit,
        async_report_threshold: Optional[float],
        nameplate_max_value: Optional[int],
    ):
        self.tuple = TelemetryReportingConfig(
            TelemetryName=telemetry_name,
            AboutNodeName=about_node_name,
            ReportOnChange=report_on_change,
            SamplePeriodS=sample_period_s,
            Exponent=exponent,
            Unit=unit,
            AsyncReportThreshold=async_report_threshold,
            NameplateMaxValue=nameplate_max_value,
        )

    @classmethod
    def tuple_to_type(cls, tuple: TelemetryReportingConfig) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> TelemetryReportingConfig:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> TelemetryReportingConfig:
        """
        Deserialize a dictionary representation of a telemetry.reporting.config.000 message object
        into a TelemetryReportingConfig python object for internal use.

        This is the near-inverse of the TelemetryReportingConfig.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a SchemaError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           SchemaError: if the dict cannot be turned into a TelemetryReportingConfig object.

        Returns:
            TelemetryReportingConfig
        """
        d2 = dict(d)
        if "TelemetryNameGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"TelemetryNameGtEnumSymbol missing from dict <{d2}>")
        value = EnumTelemetryName.symbol_to_value(d2["TelemetryNameGtEnumSymbol"])
        d2["TelemetryName"] = EnumTelemetryName(value)
        if "AboutNodeName" not in d2.keys():
            raise SchemaError(f"dict missing AboutNodeName: <{d2}>")
        if "ReportOnChange" not in d2.keys():
            raise SchemaError(f"dict missing ReportOnChange: <{d2}>")
        if "SamplePeriodS" not in d2.keys():
            raise SchemaError(f"dict missing SamplePeriodS: <{d2}>")
        if "Exponent" not in d2.keys():
            raise SchemaError(f"dict missing Exponent: <{d2}>")
        if "UnitGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"UnitGtEnumSymbol missing from dict <{d2}>")
        value = EnumUnit.symbol_to_value(d2["UnitGtEnumSymbol"])
        d2["Unit"] = EnumUnit(value)
        if "TypeName" not in d2.keys():
            raise SchemaError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise SchemaError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "000":
            LOGGER.debug(
                f"Attempting to interpret telemetry.reporting.config version {d2['Version']} as version 000"
            )
            d2["Version"] = "000"
        return TelemetryReportingConfig(**d2)


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


def check_is_positive_integer(v: int) -> None:
    """
    Must be positive when interpreted as an integer. Interpretation as an
    integer follows the pydantic rules for this - which will round down
    rational numbers. So 1.7 will be interpreted as 1 and is also fine,
    while 0.5 is interpreted as 0 and will raise an exception.

    Args:
        v (int): the candidate

    Raises:
        ValueError: if v < 1
    """
    v2 = int(v)
    if v2 < 1:
        raise ValueError(f"<{v}> is not PositiveInteger")
