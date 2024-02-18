"""Type electric.meter.component.gt, version 000"""
import json
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from gwproto.data_classes.components.electric_meter_component import (
    ElectricMeterComponent,
)
from gwproto.errors import SchemaError
from gwproto.types.egauge_io import EgaugeIo
from gwproto.types.egauge_io import EgaugeIo_Maker
from gwproto.types.telemetry_reporting_config import TelemetryReportingConfig
from gwproto.types.telemetry_reporting_config import TelemetryReportingConfig_Maker


LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)
LOGGER = logging.getLogger(__name__)


class ElectricMeterComponentGt(BaseModel):
    """
    Type for tracking Electric Meter Components.

    Designed for specific instances of Electric Meters. It extends the component.gt.000 type.
    Authority for the attributes of the component.gt.000 (ComponentId, ComponentAttributeClassId,
    DisplayName, HwUid) belongs to the WorldRegistry. The WorldRegistry is part of the GridWorks
    'BackOffice' structure for managing relational device data . Notably, ComponentId and ComponentAttributeClass
    are both required and immutable. HwUid is optional but once it is set to a non-null value
    that is also immutable - it is meant to be an immutable identifier associated to a specific
    physical device, ideally one that can be read remotely by the SCADA and also by the naked
    eye. The DisplayName is mutable, with its current value in time governed by the WorldRegistry.

    [More info](https://g-node-registry.readthedocs.io/en/latest/electric-meters.html)
    """

    ComponentId: str = Field(
        title="Component Id",
        description=(
            "Primary GridWorks identifier for a specific physical instance of an ElectricMeter, "
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
    DisplayName: Optional[str] = Field(
        title="Display Name for the Power Meter",
        description="Sample: Oak EGauge6074",
        default=None,
    )
    ConfigList: List[TelemetryReportingConfig] = Field(
        title="List of Data Channel configs ",
        description=(
            "This power meter will produce multiple data channels. Each data channel measures "
            "a certain quantities (like power, current) for certain ShNodes (like a boost element "
            "or heat pump)."
        ),
    )
    HwUid: Optional[str] = Field(
        title="Unique Hardware Id for the Power Meter",
        description="For eGauge, use what comes back over modbus address 100.",
        default=None,
    )
    ModbusHost: Optional[str] = Field(
        title="Host on LAN when power meter is modbus over Ethernet",
        default=None,
    )
    ModbusPort: Optional[int] = Field(
        title="ModbusPort",
        default=None,
    )
    EgaugeIoList: List[EgaugeIo] = Field(
        title="Bijecton from EGauge4030 input to ConfigList output",
        description=(
            "This should be empty unless the MakeModel of the corresponding component attribute "
            "class is EGauge 4030. The channels that can be read from an EGauge 4030 are configurable "
            "by the person who installs the device. The information is encapsulated in a modbus "
            "map provided by eGauge as a csv from a device-specific API. The EGaugeIoList maps "
            "the data from this map to the data that the SCADA expects to see."
        ),
    )
    TypeName: Literal["electric.meter.component.gt"] = "electric.meter.component.gt"
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

    @validator("ModbusPort")
    def _check_modbus_port(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        try:
            check_is_non_negative_integer(v)
        except ValueError as e:
            raise ValueError(
                f"ModbusPort failed NonNegativeInteger format validation: {e}"
            )
        return v

    @root_validator
    def check_axiom_1(cls, v: dict) -> dict:
        """
        Axiom 1: Modbus consistency.
        ModbusHost is None if and only if ModbusPort is None
        """
        # TODO: Implement check for axiom 1"
        ModbusHost = v.get("ModbusHost", None)
        ModbusPort = v.get("ModbusHost", None)
        if ModbusHost is None and not (ModbusPort is None):
            raise ValueError("Axiom 1: ModbusHost None iff ModbusPort None! ")
        if not (ModbusHost is None) and ModbusPort is None:
            raise ValueError("Axiom 1: ModbusHost None iff ModbusPort None! ")
        return v

    @root_validator
    def check_axiom_2(cls, v: dict) -> dict:
        """
        Axiom 2: Egauge4030 consistency.
        If the EgaugeIoList has non-zero length, then the ModbusHost is not None and
        the set of output configs is equal to ConfigList as a set
        """
        # TODO: Implement check for axiom 2"
        EgaugeIoList = v.get("EgaugeIoList", None)
        ModbusHost = v.get("ModbusHost", None)
        ConfigList = v.get("ConfigList", None)
        if len(EgaugeIoList) == 0:
            return v

        if ModbusHost is None:
            raise ValueError(
                f"Axiom 2: If EgaugeIoList has non-zero length then ModbusHost must exist!"
            )
        output_configs = set(map(lambda x: x.OutputConfig, EgaugeIoList))
        if output_configs != set(ConfigList):
            raise ValueError(
                "Axiom 2: If EgaugeIoList has non-zero length then then the set of"
                "output configs must equal ConfigList as a set"
            )
        return v

    def as_dict(self) -> Dict[str, Any]:
        """
        Translate the object into a dictionary representation that can be serialized into a
        electric.meter.component.gt.000 object.

        This method prepares the object for serialization by the as_type method, creating a
        dictionary with key-value pairs that follow the requirements for an instance of the
        electric.meter.component.gt.000 type. Unlike the standard python dict method,
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
        config_list = []
        for elt in self.ConfigList:
            config_list.append(elt.as_dict())
        d["ConfigList"] = config_list
        # Recursively calling as_dict()
        egauge_io_list = []
        for elt in self.EgaugeIoList:
            egauge_io_list.append(elt.as_dict())
        d["EgaugeIoList"] = egauge_io_list
        return d

    def as_type(self) -> bytes:
        """
        Serialize to the electric.meter.component.gt.000 representation.

        Instances in the class are python-native representations of electric.meter.component.gt.000
        objects, while the actual electric.meter.component.gt.000 object is the serialized UTF-8 byte
        string designed for sending in a message.

        This method calls the as_dict() method, which differs from the native python dict()
        in the following key ways:
        - Enum Values: Translates between the values used locally by the actor to the symbol
        sent in messages.
        - - Removes any key-value pairs where the value is None for a clearer message, especially
        in cases with many optional attributes.

        It also applies these changes recursively to sub-types.

        Its near-inverse is ElectricMeterComponentGt.type_to_tuple(). If the type (or any sub-types)
        includes an enum, then the type_to_tuple will map an unrecognized symbol to the
        default enum value. This is why these two methods are only 'near' inverses.
        """
        json_string = json.dumps(self.as_dict())
        return json_string.encode("utf-8")

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))  # noqa


class ElectricMeterComponentGt_Maker:
    type_name = "electric.meter.component.gt"
    version = "000"

    def __init__(
        self,
        component_id: str,
        component_attribute_class_id: str,
        display_name: Optional[str],
        config_list: List[TelemetryReportingConfig],
        hw_uid: Optional[str],
        modbus_host: Optional[str],
        modbus_port: Optional[int],
        egauge_io_list: List[EgaugeIo],
    ):
        self.tuple = ElectricMeterComponentGt(
            ComponentId=component_id,
            ComponentAttributeClassId=component_attribute_class_id,
            DisplayName=display_name,
            ConfigList=config_list,
            HwUid=hw_uid,
            ModbusHost=modbus_host,
            ModbusPort=modbus_port,
            EgaugeIoList=egauge_io_list,
        )

    @classmethod
    def tuple_to_type(cls, tuple: ElectricMeterComponentGt) -> bytes:
        """
        Given a Python class object, returns the serialized JSON type object.
        """
        return tuple.as_type()

    @classmethod
    def type_to_tuple(cls, t: bytes) -> ElectricMeterComponentGt:
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
    def dict_to_tuple(cls, d: dict[str, Any]) -> ElectricMeterComponentGt:
        """
        Deserialize a dictionary representation of a electric.meter.component.gt.000 message object
        into a ElectricMeterComponentGt python object for internal use.

        This is the near-inverse of the ElectricMeterComponentGt.as_dict() method:
          - Enums: translates between the symbols sent in messages between actors and
        the values used by the actors internally once they've deserialized the messages.
          - Types: recursively validates and deserializes sub-types.

        Note that if a required attribute with a default value is missing in a dict, this method will
        raise a SchemaError. This differs from the pydantic BaseModel practice of auto-completing
        missing attributes with default values when they exist.

        Args:
            d (dict): the dictionary resulting from json.loads(t) for a serialized JSON type object t.

        Raises:
           SchemaError: if the dict cannot be turned into a ElectricMeterComponentGt object.

        Returns:
            ElectricMeterComponentGt
        """
        d2 = dict(d)
        if "ComponentId" not in d2.keys():
            raise SchemaError(f"dict missing ComponentId: <{d2}>")
        if "ComponentAttributeClassId" not in d2.keys():
            raise SchemaError(f"dict missing ComponentAttributeClass: <{d2}>")
        if "ConfigList" not in d2.keys():
            raise SchemaError(f"dict missing ConfigList: <{d2}>")
        if not isinstance(d2["ConfigList"], List):
            raise SchemaError(f"ConfigList <{d2['ConfigList']}> must be a List!")
        config_list = []
        for elt in d2["ConfigList"]:
            if not isinstance(elt, dict):
                raise SchemaError(
                    f"ConfigList <{d2['ConfigList']}> must be a List of TelemetryReportingConfig types"
                )
            t = TelemetryReportingConfig_Maker.dict_to_tuple(elt)
            config_list.append(t)
        d2["ConfigList"] = config_list
        if "EgaugeIoList" not in d2.keys():
            raise SchemaError(f"dict missing EgaugeIoList: <{d2}>")
        if not isinstance(d2["EgaugeIoList"], List):
            raise SchemaError(f"EgaugeIoList <{d2['EgaugeIoList']}> must be a List!")
        egauge_io_list = []
        for elt in d2["EgaugeIoList"]:
            if not isinstance(elt, dict):
                raise SchemaError(
                    f"EgaugeIoList <{d2['EgaugeIoList']}> must be a List of EgaugeIo types"
                )
            t = EgaugeIo_Maker.dict_to_tuple(elt)
            egauge_io_list.append(t)
        d2["EgaugeIoList"] = egauge_io_list
        if "TypeName" not in d2.keys():
            raise SchemaError(f"TypeName missing from dict <{d2}>")
        if "Version" not in d2.keys():
            raise SchemaError(f"Version missing from dict <{d2}>")
        if d2["Version"] != "000":
            LOGGER.debug(
                f"Attempting to interpret electric.meter.component.gt version {d2['Version']} as version 000"
            )
            d2["Version"] = "000"
        return ElectricMeterComponentGt(**d2)

    @classmethod
    def tuple_to_dc(cls, t: ElectricMeterComponentGt) -> ElectricMeterComponent:
        if t.ComponentId in ElectricMeterComponent.by_id.keys():
            dc = ElectricMeterComponent.by_id[t.ComponentId]
        else:
            dc = ElectricMeterComponent(
                component_id=t.ComponentId,
                component_attribute_class_id=t.ComponentAttributeClassId,
                display_name=t.DisplayName,
                config_list=t.ConfigList,
                hw_uid=t.HwUid,
                modbus_host=t.ModbusHost,
                modbus_port=t.ModbusPort,
                egauge_io_list=t.EgaugeIoList,
            )
        return dc

    @classmethod
    def dc_to_tuple(cls, dc: ElectricMeterComponent) -> ElectricMeterComponentGt:
        t = ElectricMeterComponentGt_Maker(
            component_id=dc.component_id,
            component_attribute_class_id=dc.component_attribute_class_id,
            display_name=dc.display_name,
            config_list=dc.config_list,
            hw_uid=dc.hw_uid,
            modbus_host=dc.modbus_host,
            modbus_port=dc.modbus_port,
            egauge_io_list=dc.egauge_io_list,
        ).tuple
        return t

    @classmethod
    def type_to_dc(cls, t: str) -> ElectricMeterComponent:
        return cls.tuple_to_dc(cls.type_to_tuple(t))

    @classmethod
    def dc_to_type(cls, dc: ElectricMeterComponent) -> str:
        return cls.dc_to_tuple(dc).as_type()

    @classmethod
    def dict_to_dc(cls, d: dict[Any, str]) -> ElectricMeterComponent:
        return cls.tuple_to_dc(cls.dict_to_tuple(d))


def check_is_non_negative_integer(v: int) -> None:
    """
    Must be non-negative when interpreted as an integer. Interpretation
    as an integer follows the pydantic rules for this - which will round
    down rational numbers. So 0 is fine, and 1.7 will be interpreted as
    1 and is also fine.

    Args:
        v (int): the candidate

    Raises:
        ValueError: if v < 0
    """
    v2 = int(v)
    if v2 < 0:
        raise ValueError(f"<{v}> is not NonNegativeInteger")


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
