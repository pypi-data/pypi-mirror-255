from enum import auto
from typing import List

from fastapi_utils.enums import StrEnum


class Role(StrEnum):
    """
    Categorizes SpaceheatNodes by their function within the heating system

    Enum sh.node.role version 000 in the GridWorks Type registry.

    Used by used by multiple Application Shared Languages (ASLs), including but not limited to
    gwproto. For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#shnoderole)
      - [More Info](https://gridworks-protocol.readthedocs.io/en/latest/spaceheat-node-role.html)

    Values (with symbols in parens):
      - Unknown (00000000): Unknown Role
      - Scada (d0afb424): Primary SCADA
      - HomeAlone (863e50d1): HomeAlone GNode
      - Atn (6ddff83b): AtomicTNode
      - PowerMeter (9ac68b6e): A SpaceheatNode representing the power meter that is used to settle
        financial transactions with the TerminalAsset. That is, this is the power meter whose
        accuracy is certified in the creation of the TerminalAsset GNode via creation of the
        TaDeed. [More Info](https://gridworks.readthedocs.io/en/latest/terminal-asset.html).
      - BoostElement (99c5f326): Resistive element used for providing heat to a thermal store.
      - BooleanActuator (57b788ee): A solid state or mechanical relay with two states (open, closed)
      - DedicatedThermalStore (3ecfe9b8): A dedicated thermal store within a thermal storage heating
        system - could be one or more water tanks, phase change material, etc.
      - TankWaterTempSensor (73308a1f): A temperature sensor used for measuring temperature inside
        or on the immediate outside of a water tank.
      - PipeTempSensor (c480f612): A temperature sensor used for measuring the temperature of a tank.
        Typically curved metal thermistor with thermal grease for good contact.
      - RoomTempSensor (fec74958): A temperature sensor used for measuring room temperature, or temp
        in a heated space more generally.
      - OutdoorTempSensor (5938bf1f): A temperature sensor used for measuring outdoor temperature.
      - PipeFlowMeter (ece3b600): A meter that measures flow of liquid through a pipe, in units of
        VOLUME/TIME
      - HeatedSpace (65725f44): A Heated Space.
      - HydronicPipe (fe3cbdd5): A pipe carrying techinical water or other fluid (e.g. glycol) in
        a heating system.
      - BaseboardRadiator (05fdd645): A baseboard radiator - one kind of emitter in a hydronic heating
        system.
      - RadiatorFan (6896109b): A fan that can amplify the power out of a radiator.
      - CirculatorPump (b0eaf2ba): Circulator pump for one or more of the hydronic pipe loops
      - MultiChannelAnalogTempSensor (661d7e73): An analog multi channel temperature sensor
      - Outdoors (dd975b31): The outdoors
    """

    Unknown = auto()
    Scada = auto()
    HomeAlone = auto()
    Atn = auto()
    PowerMeter = auto()
    BoostElement = auto()
    BooleanActuator = auto()
    DedicatedThermalStore = auto()
    TankWaterTempSensor = auto()
    PipeTempSensor = auto()
    RoomTempSensor = auto()
    OutdoorTempSensor = auto()
    PipeFlowMeter = auto()
    HeatedSpace = auto()
    HydronicPipe = auto()
    BaseboardRadiator = auto()
    RadiatorFan = auto()
    CirculatorPump = auto()
    MultiChannelAnalogTempSensor = auto()
    Outdoors = auto()

    @classmethod
    def default(cls) -> "Role":
        """
        Returns default value (in this case Unknown)
        """
        return cls.Unknown

    @classmethod
    def values(cls) -> List[str]:
        """
        Returns enum choices
        """
        return [elt.value for elt in cls]

    @classmethod
    def version(cls, value: str) -> str:
        """
        Returns the version of an enum value.

        Once a value belongs to one version of the enum, it belongs
        to all future versions.

        Args:
            value (str): The candidate enum value.

        Raises:
            ValueError: If value is not one of the enum values.

        Returns:
            str: The earliest version of the enum containing value.
        """
        if not isinstance(value, str):
            raise ValueError(f"This method applies to strings, not enums")
        if value not in value_to_version.keys():
            raise ValueError(f"Unknown enum value: {value}")
        return value_to_version[value]

    @classmethod
    def enum_name(cls) -> str:
        """
        The name in the GridWorks Type Registry (sh.node.role)
        """
        return "sh.node.role"

    @classmethod
    def enum_version(cls) -> str:
        """
        The version in the GridWorks Type Registry (000)
        """
        return "000"

    @classmethod
    def symbol_to_value(cls, symbol: str) -> str:
        """
        Given the symbol sent in a serialized message, returns the encoded enum.

        Args:
            symbol (str): The candidate symbol.

        Returns:
            str: The encoded value associated to that symbol. If the symbol is not
            recognized - which could happen if the actor making the symbol is using
            a later version of this enum, returns the default value of "Unknown".
        """
        if symbol not in symbol_to_value.keys():
            return cls.default().value
        return symbol_to_value[symbol]

    @classmethod
    def value_to_symbol(cls, value: str) -> str:
        """
        Provides the encoding symbol for a Role enum to send in seriliazed messages.

        Args:
            symbol (str): The candidate value.

        Returns:
            str: The symbol encoding that value. If the value is not recognized -
            which could happen if the actor making the message used a later version
            of this enum than the actor decoding the message, returns the default
            symbol of "00000000".
        """
        if value not in value_to_symbol.keys():
            return value_to_symbol[cls.default().value]
        return value_to_symbol[value]

    @classmethod
    def symbols(cls) -> List[str]:
        """
        Returns a list of the enum symbols
        """
        return [
            "00000000",
            "d0afb424",
            "863e50d1",
            "6ddff83b",
            "9ac68b6e",
            "99c5f326",
            "57b788ee",
            "3ecfe9b8",
            "73308a1f",
            "c480f612",
            "fec74958",
            "5938bf1f",
            "ece3b600",
            "65725f44",
            "fe3cbdd5",
            "05fdd645",
            "6896109b",
            "b0eaf2ba",
            "661d7e73",
            "dd975b31",
        ]


symbol_to_value = {
    "00000000": "Unknown",
    "d0afb424": "Scada",
    "863e50d1": "HomeAlone",
    "6ddff83b": "Atn",
    "9ac68b6e": "PowerMeter",
    "99c5f326": "BoostElement",
    "57b788ee": "BooleanActuator",
    "3ecfe9b8": "DedicatedThermalStore",
    "73308a1f": "TankWaterTempSensor",
    "c480f612": "PipeTempSensor",
    "fec74958": "RoomTempSensor",
    "5938bf1f": "OutdoorTempSensor",
    "ece3b600": "PipeFlowMeter",
    "65725f44": "HeatedSpace",
    "fe3cbdd5": "HydronicPipe",
    "05fdd645": "BaseboardRadiator",
    "6896109b": "RadiatorFan",
    "b0eaf2ba": "CirculatorPump",
    "661d7e73": "MultiChannelAnalogTempSensor",
    "dd975b31": "Outdoors",
}

value_to_symbol = {value: key for key, value in symbol_to_value.items()}

value_to_version = {
    "Unknown": "000",
    "Scada": "000",
    "HomeAlone": "000",
    "Atn": "000",
    "PowerMeter": "000",
    "BoostElement": "000",
    "BooleanActuator": "000",
    "DedicatedThermalStore": "000",
    "TankWaterTempSensor": "000",
    "PipeTempSensor": "000",
    "RoomTempSensor": "000",
    "OutdoorTempSensor": "000",
    "PipeFlowMeter": "000",
    "HeatedSpace": "000",
    "HydronicPipe": "000",
    "BaseboardRadiator": "000",
    "RadiatorFan": "000",
    "CirculatorPump": "000",
    "MultiChannelAnalogTempSensor": "000",
    "Outdoors": "000",
}
