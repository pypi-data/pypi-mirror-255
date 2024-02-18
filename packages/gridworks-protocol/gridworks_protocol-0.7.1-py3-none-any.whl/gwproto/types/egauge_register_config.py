"""Type egauge.register.config, version 000"""
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


class EgaugeRegisterConfig(BaseModel):
    """
    Used to translate eGauge's Modbus Map.

    This type captures the information provided by eGauge in its modbus csv map, when reading
    current, power, energy, voltage, frequency etc from an eGauge 4030.
    """

    Address: int = Field(
        title="Address",
        description=(
            "EGauge's modbus holding address. Note that the EGauge modbus map for holding address "
            "100 will be 30100 - the '+30000' indicates it is a holding address. We use the 4-digit "
            "address after the '3'."
        ),
    )
    Name: str = Field(
        title="Name",
        description=(
            "The name assigned in the EGauge's modbus map. This is configured by the user (see "
            "URL)"
            "[More info](https://docs.google.com/document/d/1VeAt-V_AVqqiB0EVf-4JL_k_hVOsgbqldeAPVNwG1yI/edit#heading=h.7ct5hku166ut)"
        ),
    )
    Description: str = Field(
        title="Description",
        description="Again, assigned by the EGauge modbus map. Is usually 'change in value'",
    )
    Type: str = Field(
        title="Type",
        description=(
            "EGauge's numerical data type. Typically our power measurements are f32 ( 32-bit "
            "floating-point number). The serial number & firmware are t16 (which work to treat "
            "as 16-bit unsigned integer) and timestamps are u32 (32-bit unsigned integer)."
        ),
    )
    Denominator: int = Field(
        title="Denominator",
        description=(
            "Some of the modbus registers divide by 3.60E+06 (cumulative energy registers typically). "
            "For the power, current, voltage and phase angle the denominator is 1."
        ),
    )
    Unit: str = Field(
        title="Unit",
        description="The EGauge unit - typically A, Hz, or W.",
    )
    TypeName: Literal["egauge.register.config"] = "egauge.register.config"
    Version: Literal["000"] = "000"

    def as_dict(self) -> Dict[str, Any]:
        """
        Translate the object into a dictionary representation that can be serialized into a
        egauge.register.config.000 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        egauge.register.config.000 type. Unlike the standard python dict method,
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
        Serialize to the egauge.register.config.000 representation.

        Instances in the class are python-native representations of egauge.register.config.000
        objects, while the actual egauge.register.config.000 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is EgaugeRegisterConfig.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class EgaugeRegisterConfig_Maker:
    type_name = "egauge.register.config"
    version = "000"

    def __init__(
        self,
        address: int,
        name: str,
        description: str,
        type: str,
        denominator: int,
        unit: str,
    ):
        self.tuple = EgaugeRegisterConfig(
            Address=address,
            Name=name,
            Description=description,
            Type=type,
            Denominator=denominator,
            Unit=unit,
        )

    @classmethod
    def tuple_to_type(cls, tuple: EgaugeRegisterConfig) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> EgaugeRegisterConfig:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> EgaugeRegisterConfig:
        """
        Deserialize a dictionary representation of a egauge.register.config.000 message object
        into a EgaugeRegisterConfig python object for internal use.

        This is the near-inverse of the EgaugeRegisterConfig.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a SchemaError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           SchemaError: if the dict cannot be turned into a EgaugeRegisterConfig object.

        Returns:
            EgaugeRegisterConfig
        """
        d2 = dict(d)
        if "Address" not in d2.keys():
            raise SchemaError(f"dict missing Address: <{d2}>")
        if "Name" not in d2.keys():
            raise SchemaError(f"dict missing Name: <{d2}>")
        if "Description" not in d2.keys():
            raise SchemaError(f"dict missing Description: <{d2}>")
        if "Type" not in d2.keys():
            raise SchemaError(f"dict missing Type: <{d2}>")
        if "Denominator" not in d2.keys():
            raise SchemaError(f"dict missing Denominator: <{d2}>")
        if "Unit" not in d2.keys():
            raise SchemaError(f"dict missing Unit: <{d2}>")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise SchemaError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "000":
            LOGGER.debug(
                f"Attempting to interpret egauge.register.config version {d2['Version']} as version 000"
            )
            d2["Version"] = "000"
        return EgaugeRegisterConfig(**d2)
