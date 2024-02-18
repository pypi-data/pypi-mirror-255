"""Type ta.data.channels, version 000"""
import json
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Literal

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from gwproto.errors import SchemaError
from gwproto.types.data_channel import DataChannel
from gwproto.types.data_channel import DataChannel_Maker


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class TaDataChannels(BaseModel):
    """
    Terminal Asset Data Channels.

    A list of data channels associated to a specific Terminal Asset.
    """

    TerminalAssetGNodeAlias: str = Field(
        title="GNodeAlias for the Terminal Asset",
        description=(
            "The Alias of the Terminal Asset about which the time series data is providing information."
        ),
    )
    TerminalAssetGNodeId: str = Field(
        title="GNodeId for the Terminal Asset",
        description="The immutable unique identifier for the Terminal Asset.",
    )
    TimeUnixS: int = Field(
        title="TimeUnixS",
        description="The time that this list of data channels was created",
    )
    Author: str = Field(
        title="Author",
        description="Author of this list of data channels.",
    )
    Channels: List[DataChannel] = Field(
        title="The list of data channels",
    )
    Identifier: str = Field(
        title="Identifier",
        description=(
            "Unique identifier for a specific instance of this type that can be used to establish "
            "how time series csv's were constructed."
        ),
    )
    TypeName: Literal["ta.data.channels"] = "ta.data.channels"
    Version: Literal["000"] = "000"

    @validator("TerminalAssetGNodeAlias")
    def _check_terminal_asset_g_node_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(
                f"TerminalAssetGNodeAlias failed LeftRightDot format validation: {e}"
            )
        return v

    @validator("TerminalAssetGNodeId")
    def _check_terminal_asset_g_node_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"TerminalAssetGNodeId failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    @validator("TimeUnixS")
    def _check_time_unix_s(cls, v: int) -> int:
        try:
            check_is_reasonable_unix_time_s(v)
        except ValueError as e:
            raise ValueError(
                f"TimeUnixS failed ReasonableUnixTimeS format validation: {e}"
            )
        return v

    @validator("Identifier")
    def _check_identifier(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"Identifier failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        """
        Translate the object into a dictionary representation that can be serialized into a
        ta.data.channels.000 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        ta.data.channels.000 type. Unlike the standard python dict method,
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
        channels = []
        for elt in self.Channels:
            channels.append(elt.as_dict())
        d["Channels"] = channels
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the ta.data.channels.000 representation.

        Instances in the class are python-native representations of ta.data.channels.000
        objects, while the actual ta.data.channels.000 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is TaDataChannels.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class TaDataChannels_Maker:
    type_name = "ta.data.channels"
    version = "000"

    def __init__(
        self,
        terminal_asset_g_node_alias: str,
        terminal_asset_g_node_id: str,
        time_unix_s: int,
        author: str,
        channels: List[DataChannel],
        identifier: str,
    ):
        self.tuple = TaDataChannels(
            TerminalAssetGNodeAlias=terminal_asset_g_node_alias,
            TerminalAssetGNodeId=terminal_asset_g_node_id,
            TimeUnixS=time_unix_s,
            Author=author,
            Channels=channels,
            Identifier=identifier,
        )

    @classmethod
    def tuple_to_type(cls, tuple: TaDataChannels) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> TaDataChannels:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> TaDataChannels:
        """
        Deserialize a dictionary representation of a ta.data.channels.000 message object
        into a TaDataChannels python object for internal use.

        This is the near-inverse of the TaDataChannels.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a SchemaError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           SchemaError: if the dict cannot be turned into a TaDataChannels object.

        Returns:
            TaDataChannels
        """
        d2 = dict(d)
        if "TerminalAssetGNodeAlias" not in d2.keys():
            raise SchemaError(f"dict missing TerminalAssetGNodeAlias: <{d2}>")
        if "TerminalAssetGNodeId" not in d2.keys():
            raise SchemaError(f"dict missing TerminalAssetGNodeId: <{d2}>")
        if "TimeUnixS" not in d2.keys():
            raise SchemaError(f"dict missing TimeUnixS: <{d2}>")
        if "Author" not in d2.keys():
            raise SchemaError(f"dict missing Author: <{d2}>")
        if "Channels" not in d2.keys():
            raise SchemaError(f"dict missing Channels: <{d2}>")
        if not isinstance(d2["Channels"], List):
            raise SchemaError(f"Channels <{d2['Channels']}> must be a List!")
        channels = []
        for elt in d2["Channels"]:
            if not isinstance(elt, dict):
                raise SchemaError(
                    f"Channels <{d2['Channels']}> must be a List of DataChannel types"
                )
            t = DataChannel_Maker.dict_to_tuple(elt)
            channels.append(t)
        d2["Channels"] = channels
        if "Identifier" not in d2.keys():
            raise SchemaError(f"dict missing Identifier: <{d2}>")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise SchemaError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "000":
            LOGGER.debug(
                f"Attempting to interpret ta.data.channels version {d2['Version']} as version 000"
            )
            d2["Version"] = "000"
        return TaDataChannels(**d2)


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


def check_is_reasonable_unix_time_s(v: int) -> None:
    """Checks ReasonableUnixTimeS format

    ReasonableUnixTimeS format: unix seconds between Jan 1 2000 and Jan 1 3000

    Args:
        v (int): the candidate

    Raises:
        ValueError: if v is not ReasonableUnixTimeS format
    """
    import pendulum

    if pendulum.parse("2000-01-01T00:00:00Z").int_timestamp > v:  # type: ignore[attr-defined]
        raise ValueError(f"<{v}> must be after Jan 1 2000")
    if pendulum.parse("3000-01-01T00:00:00Z").int_timestamp < v:  # type: ignore[attr-defined]
        raise ValueError(f"<{v}> must be before Jan 1 3000")


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
