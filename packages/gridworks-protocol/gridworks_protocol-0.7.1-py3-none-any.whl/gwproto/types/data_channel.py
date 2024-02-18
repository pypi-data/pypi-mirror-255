"""Type data.channel, version 000"""
import json
import logging
from typing import Any
from typing import Dict
from typing import Literal

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from gwproto.enums import TelemetryName as EnumTelemetryName
from gwproto.errors import SchemaError


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class DataChannel(BaseModel):
    """
    Data Channel.

    A data channel is a concept of some collection of readings that share all characteristics
    other than time.
    """

    DisplayName: str = Field(
        title="Display Name",
        description=(
            "This display name is the handle for the data channel. It is meant to be set by the "
            "person/people who will be analyzing time series data. It is only expected to be "
            "unique within the data channels associated to a specific Terminal Asset."
        ),
    )
    AboutName: str = Field(
        title="About Name",
        description="The name of the SpaceheatNode whose physical quantities are getting captured.",
    )
    CapturedByName: str = Field(
        title="CapturedByName",
        description=(
            "The name of the SpaceheatNode that is capturing the physical quantities (which can "
            "be AboutName but does not have to be)."
        ),
    )
    TelemetryName: EnumTelemetryName = Field(
        title="TelemetryName",
        description="The name of the physical quantity getting measured.",
    )
    TypeName: Literal["data.channel"] = "data.channel"
    Version: Literal["000"] = "000"

    @validator("AboutName")
    def _check_about_name(cls, v: str) -> str:
        try:
            check_is_spaceheat_name(v)
        except ValueError as e:
            raise ValueError(f"AboutName failed SpaceheatName format validation: {e}")
        return v

    @validator("CapturedByName")
    def _check_captured_by_name(cls, v: str) -> str:
        try:
            check_is_spaceheat_name(v)
        except ValueError as e:
            raise ValueError(
                f"CapturedByName failed SpaceheatName format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        """
        Translate the object into a dictionary representation that can be serialized into a
        data.channel.000 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        data.channel.000 type. Unlike the standard python dict method,
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
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the data.channel.000 representation.

        Instances in the class are python-native representations of data.channel.000
        objects, while the actual data.channel.000 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is DataChannel.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class DataChannel_Maker:
    type_name = "data.channel"
    version = "000"

    def __init__(
        self,
        display_name: str,
        about_name: str,
        captured_by_name: str,
        telemetry_name: EnumTelemetryName,
    ):
        self.tuple = DataChannel(
            DisplayName=display_name,
            AboutName=about_name,
            CapturedByName=captured_by_name,
            TelemetryName=telemetry_name,
        )

    @classmethod
    def tuple_to_type(cls, tuple: DataChannel) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> DataChannel:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> DataChannel:
        """
        Deserialize a dictionary representation of a data.channel.000 message object
        into a DataChannel python object for internal use.

        This is the near-inverse of the DataChannel.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a SchemaError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           SchemaError: if the dict cannot be turned into a DataChannel object.

        Returns:
            DataChannel
        """
        d2 = dict(d)
        if "DisplayName" not in d2.keys():
            raise SchemaError(f"dict missing DisplayName: <{d2}>")
        if "AboutName" not in d2.keys():
            raise SchemaError(f"dict missing AboutName: <{d2}>")
        if "CapturedByName" not in d2.keys():
            raise SchemaError(f"dict missing CapturedByName: <{d2}>")
        if "TelemetryNameGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"TelemetryNameGtEnumSymbol missing from dict <{d2}>")
        value = EnumTelemetryName.symbol_to_value(d2["TelemetryNameGtEnumSymbol"])
        d2["TelemetryName"] = EnumTelemetryName(value)
        if "TypeName" not in d2.keys():
            raise SchemaError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise SchemaError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "000":
            LOGGER.debug(
                f"Attempting to interpret data.channel version {d2['Version']} as version 000"
            )
            d2["Version"] = "000"
        return DataChannel(**d2)


def check_is_spaceheat_name(v: str) -> None:
    """Check SpaceheatName Format.

    Validates if the provided string adheres to the SpaceheatName format:
    Lowercase words separated by periods, where word characters can be alphanumeric
    or a hyphen, and the first word starts with an alphabet character.

    Args:
        candidate (str): The string to be validated.

    Raises:
        ValueError: If the provided string is not in SpaceheatName format.
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
        for char in word:
            if not (char.isalnum() or char == "-"):
                raise ValueError(
                    f"words of <{v}> split by by '.' must be alphanumeric or hyphen."
                )
    if not v.islower():
        raise ValueError(f"<{v}> must be lowercase.")
