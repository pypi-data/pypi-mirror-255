"""Type component.attribute.class.gt, version 000"""
import json
import logging
from typing import Any
from typing import Dict
from typing import Literal
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from gwproto.data_classes.component_attribute_class import ComponentAttributeClass
from gwproto.errors import SchemaError


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class ComponentAttributeClassGt(BaseModel):
    """
    Component Attribute Class Gt.

    Authority for the attributes of the component.attribute.class.gt.000 belongs to the WorldRegistry.
    The WorldRegistry is part of the GridWorks 'BackOffice' structure for managing relational
    device data. Generally speaking, a component attribute class is meant to specify WHAT you
    might order from a plumbing supply store to 'get the same part.' The Component refers to
    something that will have a specific serial number.

    [More info](https://g-node-registry.readthedocs.io/en/latest/component-attribute-class.html)
    """

    ComponentAttributeClassId: str = Field(
        title="ComponentAttributeClassId",
        description=(
            "Unique identifier for the device class (aka 'cac' or Component Attribute Class). "
            "This identifier is used to associate a make/model with a specific component (i.e. "
            "the component will point to its ComponentAttributeClassId)."
        ),
    )
    DisplayName: Optional[str] = Field(
        title="DisplayName",
        description=(
            "Optional Mutable field to include manufacturer's model name. Note that several different "
            "models may be given the same spaceheat.make.model enum name."
        ),
        default=None,
    )
    TypeName: Literal["component.attribute.class.gt"] = "component.attribute.class.gt"
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
        component.attribute.class.gt.000 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        component.attribute.class.gt.000 type. Unlike the standard python dict method,
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
                include=self.__fields_set__ | {"TypeName", "Version"},
                by_alias=True,
            ).items()
            if value is not None
        }
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the component.attribute.class.gt.000 representation.

        Instances in the class are python-native representations of component.attribute.class.gt.000
        objects, while the actual component.attribute.class.gt.000 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is ComponentAttributeClassGt.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class ComponentAttributeClassGt_Maker:
    type_name = "component.attribute.class.gt"
    version = "000"

    def __init__(
        self,
        component_attribute_class_id: str,
        display_name: Optional[str],
    ):
        self.tuple = ComponentAttributeClassGt(
            ComponentAttributeClassId=component_attribute_class_id,
            DisplayName=display_name,
        )

    @classmethod
    def tuple_to_type(cls, tuple_: ComponentAttributeClassGt) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple_.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> ComponentAttributeClassGt:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> ComponentAttributeClassGt:
        """
        Deserialize a dictionary representation of a component.attribute.class.gt.000 message object
        into a ComponentAttributeClassGt python object for internal use.

        This is the near-inverse of the ComponentAttributeClassGt.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a SchemaError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           SchemaError: if the dict cannot be turned into a ComponentAttributeClassGt object.

        Returns:
            ComponentAttributeClassGt
        """
        d2 = dict(d)
        if "ComponentAttributeClassId" not in d2.keys():
            raise SchemaError(f"dict missing ComponentAttributeClassId: <{d2}>")
        if "TypeName" not in d2.keys():
            raise SchemaError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise SchemaError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "000":
            LOGGER.debug(
                f"Attempting to interpret component.attribute.class.gt version {d2['Version']} as version 000"
            )
            d2["Version"] = "000"
        return ComponentAttributeClassGt(**d2)

    @classmethod
    def tuple_to_dc(cls, t: ComponentAttributeClassGt) -> ComponentAttributeClass:
        if t.ComponentAttributeClassId in ComponentAttributeClass.by_id.keys():
            dc = ComponentAttributeClass.by_id[t.ComponentAttributeClassId]
        else:
            dc = ComponentAttributeClass(
                component_attribute_class_id=t.ComponentAttributeClassId,
                display_name=t.DisplayName,
            )
        return dc

    @classmethod
    def dc_to_tuple(cls, dc: ComponentAttributeClass) -> ComponentAttributeClassGt:
        t = ComponentAttributeClassGt_Maker(
            component_attribute_class_id=dc.component_attribute_class_id,
            display_name=dc.display_name,
        ).tuple
        return t

    @classmethod
    def type_to_dc(cls, t: str) -> ComponentAttributeClass:
        return cls.tuple_to_dc(cls.type_to_tuple(t))  # noqa

    @classmethod
    def dc_to_type(cls, dc: ComponentAttributeClass) -> str:
        return cls.dc_to_tuple(dc).as_type()  # noqa

    @classmethod
    def dict_to_dc(cls, d: dict[Any, str]) -> ComponentAttributeClass:
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
