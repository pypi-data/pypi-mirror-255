"""Type spaceheat.node.gt, version 100"""
import json
import logging
from typing import Any
from typing import Dict
from typing import Literal
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from gwproto.data_classes.sh_node import ShNode
from gwproto.enums import ActorClass as EnumActorClass
from gwproto.enums import Role as EnumRole
from gwproto.errors import SchemaError


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class SpaceheatNodeGt(BaseModel):
    """
    Spaceheat Node.

    A SpaceheatNode, or ShNode, is an organizing principal for the SCADA software. ShNodes can
    represent both underlying physical objects (water tank), measurements of these objects (temperature
    sensing at the top of a water tank), and actors within the code (an actor measuring multiple
    temperatures, or an actor responsible for filtering/smoothing temperature data for the purposes
    of thermostatic control).

    [More info](https://gridworks-protocol.readthedocs.io/en/latest/spaceheat-node.html)
    """

    ShNodeId: str = Field(
        title="ShNodeId",
    )
    Alias: str = Field(
        title="Alias",
    )
    ActorClass: EnumActorClass = Field(
        title="ActorClass",
    )
    Role: EnumRole = Field(
        title="Role",
    )
    DisplayName: Optional[str] = Field(
        title="DisplayName",
        default=None,
    )
    ComponentId: Optional[str] = Field(
        title="Unique identifier for Spaceheat Node's Component",
        description="Used if a Spaceheat Node is associated with a physical device.",
        default=None,
    )
    ReportingSamplePeriodS: Optional[int] = Field(
        title="ReportingSamplePeriodS",
        default=None,
    )
    RatedVoltageV: Optional[int] = Field(
        title="RatedVoltageV",
        default=None,
    )
    TypicalVoltageV: Optional[int] = Field(
        title="TypicalVoltageV",
        default=None,
    )
    InPowerMetering: Optional[bool] = Field(
        title="InPowerMetering",
        default=None,
    )
    TypeName: Literal["spaceheat.node.gt"] = "spaceheat.node.gt"
    Version: Literal["100"] = "100"

    @validator("ShNodeId")
    def _check_sh_node_id(cls, v: str) -> str:
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"ShNodeId failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    @validator("Alias")
    def _check_alias(cls, v: str) -> str:
        try:
            check_is_left_right_dot(v)
        except ValueError as e:
            raise ValueError(f"Alias failed LeftRightDot format validation: {e}")
        return v

    @validator("ComponentId")
    def _check_component_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            check_is_uuid_canonical_textual(v)
        except ValueError as e:
            raise ValueError(
                f"ComponentId failed UuidCanonicalTextual format validation: {e}"
            )
        return v

    @validator("RatedVoltageV")
    def _check_rated_voltage_v(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        try:
            check_is_positive_integer(v)
        except ValueError as e:
            raise ValueError(
                f"RatedVoltageV failed PositiveInteger format validation: {e}"
            )
        return v

    @validator("TypicalVoltageV")
    def _check_typical_voltage_v(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        try:
            check_is_positive_integer(v)
        except ValueError as e:
            raise ValueError(
                f"TypicalVoltageV failed PositiveInteger format validation: {e}"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        """
        Translate the object into a dictionary representation that can be serialized into a
        spaceheat.node.gt.100 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        spaceheat.node.gt.100 type. Unlike the standard python dict method,
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
        del d["ActorClass"]
        d["ActorClassGtEnumSymbol"] = EnumActorClass.value_to_symbol(self.ActorClass)
        del d["Role"]
        d["RoleGtEnumSymbol"] = EnumRole.value_to_symbol(self.Role)
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the spaceheat.node.gt.100 representation.

        Instances in the class are python-native representations of spaceheat.node.gt.100
        objects, while the actual spaceheat.node.gt.100 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is SpaceheatNodeGt.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class SpaceheatNodeGt_Maker:
    type_name = "spaceheat.node.gt"
    version = "100"

    def __init__(
        self,
        sh_node_id: str,
        alias: str,
        actor_class: EnumActorClass,
        role: EnumRole,
        display_name: Optional[str],
        component_id: Optional[str],
        reporting_sample_period_s: Optional[int],
        rated_voltage_v: Optional[int],
        typical_voltage_v: Optional[int],
        in_power_metering: Optional[bool],
    ):
        self.tuple = SpaceheatNodeGt(
            ShNodeId=sh_node_id,
            Alias=alias,
            ActorClass=actor_class,
            Role=role,
            DisplayName=display_name,
            ComponentId=component_id,
            ReportingSamplePeriodS=reporting_sample_period_s,
            RatedVoltageV=rated_voltage_v,
            TypicalVoltageV=typical_voltage_v,
            InPowerMetering=in_power_metering,
        )

    @classmethod
    def tuple_to_type(cls, tuple: SpaceheatNodeGt) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> SpaceheatNodeGt:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> SpaceheatNodeGt:
        """
        Deserialize a dictionary representation of a spaceheat.node.gt.100 message object
        into a SpaceheatNodeGt python object for internal use.

        This is the near-inverse of the SpaceheatNodeGt.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a SchemaError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           SchemaError: if the dict cannot be turned into a SpaceheatNodeGt object.

        Returns:
            SpaceheatNodeGt
        """
        d2 = dict(d)
        if "ShNodeId" not in d2.keys():
            raise SchemaError(f"dict missing ShNodeId: <{d2}>")
        if "Alias" not in d2.keys():
            raise SchemaError(f"dict missing Alias: <{d2}>")
        if "ActorClassGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"ActorClassGtEnumSymbol missing from dict <{d2}>")
        value = EnumActorClass.symbol_to_value(d2["ActorClassGtEnumSymbol"])
        d2["ActorClass"] = EnumActorClass(value)
        if "RoleGtEnumSymbol" not in d2.keys():
            raise SchemaError(f"RoleGtEnumSymbol missing from dict <{d2}>")
        value = EnumRole.symbol_to_value(d2["RoleGtEnumSymbol"])
        d2["Role"] = EnumRole(value)
        if "TypeName" not in d2.keys():
            raise SchemaError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise SchemaError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "100":
            LOGGER.debug(
                f"Attempting to interpret spaceheat.node.gt version {d2['Version']} as version 100"
            )
            d2["Version"] = "100"
        return SpaceheatNodeGt(**d2)

    @classmethod
    def tuple_to_dc(cls, t: SpaceheatNodeGt) -> ShNode:
        if t.ShNodeId in ShNode.by_id.keys():
            dc = ShNode.by_id[t.ShNodeId]
        else:
            dc = ShNode(
                sh_node_id=t.ShNodeId,
                alias=t.Alias,
                actor_class=t.ActorClass,
                role=t.Role,
                display_name=t.DisplayName,
                component_id=t.ComponentId,
                reporting_sample_period_s=t.ReportingSamplePeriodS,
                rated_voltage_v=t.RatedVoltageV,
                typical_voltage_v=t.TypicalVoltageV,
                in_power_metering=t.InPowerMetering,
            )
        return dc

    @classmethod
    def dc_to_tuple(cls, dc: ShNode) -> SpaceheatNodeGt:
        t = SpaceheatNodeGt_Maker(
            sh_node_id=dc.sh_node_id,
            alias=dc.alias,
            actor_class=dc.actor_class,
            role=dc.role,
            display_name=dc.display_name,
            component_id=dc.component_id,
            reporting_sample_period_s=dc.reporting_sample_period_s,
            rated_voltage_v=dc.rated_voltage_v,
            typical_voltage_v=dc.typical_voltage_v,
            in_power_metering=dc.in_power_metering,
        ).tuple
        return t

    @classmethod
    def type_to_dc(cls, t: str) -> ShNode:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: ShNode) -> str:
        return cls.dc_to_tuple(dc).as_type()

    @classmethod
    def dict_to_dc(cls, d: dict[Any, str]) -> ShNode:
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
