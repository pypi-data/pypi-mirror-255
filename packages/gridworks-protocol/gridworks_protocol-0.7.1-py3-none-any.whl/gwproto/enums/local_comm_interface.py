from enum import auto
from typing import List

from fastapi_utils.enums import StrEnum


class LocalCommInterface(StrEnum):
    """
    Categorization of in-house comm mechanisms for SCADA

    Enum local.comm.interface version 000 in the GridWorks Type registry.

    Used by used by multiple Application Shared Languages (ASLs), including but not limited to
    gwproto. For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#localcomminterface)

    Values (with symbols in parens):
      - Unknown (00000000)
      - I2C (9ec8bc49)
      - Ethernet (c1e7a955)
      - OneWire (ae2d4cd8)
      - RS485 (a6a4ac9f)
      - SimRabbit (efc144cd)
      - Wifi (46ac6589)
      - Analog_4_20_mA (653c73b8)
      - RS232 (0843a726)
    """

    UNKNOWN = auto()
    I2C = auto()
    ETHERNET = auto()
    ONEWIRE = auto()
    RS485 = auto()
    SIMRABBIT = auto()
    WIFI = auto()
    ANALOG_4_20_MA = auto()
    RS232 = auto()

    @classmethod
    def default(cls) -> "LocalCommInterface":
        """
        Returns default value (in this case UNKNOWN)
        """
        return cls.UNKNOWN

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
        The name in the GridWorks Type Registry (local.comm.interface)
        """
        return "local.comm.interface"

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
        Provides the encoding symbol for a LocalCommInterface enum to send in seriliazed messages.

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
            "9ec8bc49",
            "c1e7a955",
            "ae2d4cd8",
            "a6a4ac9f",
            "efc144cd",
            "46ac6589",
            "653c73b8",
            "0843a726",
        ]


symbol_to_value = {
    "00000000": "UNKNOWN",
    "9ec8bc49": "I2C",
    "c1e7a955": "ETHERNET",
    "ae2d4cd8": "ONEWIRE",
    "a6a4ac9f": "RS485",
    "efc144cd": "SIMRABBIT",
    "46ac6589": "WIFI",
    "653c73b8": "ANALOG_4_20_MA",
    "0843a726": "RS232",
}

value_to_symbol = {value: key for key, value in symbol_to_value.items()}

value_to_version = {
    "UNKNOWN": "000",
    "I2C": "000",
    "ETHERNET": "000",
    "ONEWIRE": "000",
    "RS485": "000",
    "SIMRABBIT": "000",
    "WIFI": "000",
    "ANALOG_4_20_MA": "000",
    "RS232": "000",
}
