"""Type power.watts, version 000"""
import json
import logging
from typing import Any
from typing import Dict
from typing import Literal

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from gwproto.errors import SchemaError


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class PowerWatts(BaseModel):
    """
    Real-time power of TerminalAsset in Watts.

    Used by a SCADA -> Atn or Atn -> AggregatedTNode to report real-time power of their TerminalAsset.
    Positive number means WITHDRAWAL from the grid - so generating electricity creates a negative
    number. This message is considered worse than useless to send after the first attempt, and
    does not require an ack. Shares the same purpose as gs.pwr, but is not designed to minimize
    bytes so comes in JSON format.
    """

    Watts: int = Field(
        title="Current Power in Watts",
    )
    TypeName: Literal["power.watts"] = "power.watts"
    Version: Literal["000"] = "000"

    def as_dict(self) -> Dict[str, Any]:
        """
        Translate the object into a dictionary representation that can be serialized into a
        power.watts.000 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        power.watts.000 type. Unlike the standard python dict method,
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
        Serialize to the power.watts.000 representation.

        Instances in the class are python-native representations of power.watts.000
        objects, while the actual power.watts.000 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is PowerWatts.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class PowerWatts_Maker:
    type_name = "power.watts"
    version = "000"

    def __init__(
        self,
        watts: int,
    ):
        self.tuple = PowerWatts(
            Watts=watts,
        )

    @classmethod
    def tuple_to_type(cls, tuple: PowerWatts) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> PowerWatts:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> PowerWatts:
        """
        Deserialize a dictionary representation of a power.watts.000 message object
        into a PowerWatts python object for internal use.

        This is the near-inverse of the PowerWatts.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a SchemaError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           SchemaError: if the dict cannot be turned into a PowerWatts object.

        Returns:
            PowerWatts
        """
        d2 = dict(d)
        if "Watts" not in d2.keys():
            raise SchemaError(f"dict missing Watts: <{d2}>")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise SchemaError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "000":
            LOGGER.debug(
                f"Attempting to interpret power.watts version {d2['Version']} as version 000"
            )
            d2["Version"] = "000"
        return PowerWatts(**d2)
