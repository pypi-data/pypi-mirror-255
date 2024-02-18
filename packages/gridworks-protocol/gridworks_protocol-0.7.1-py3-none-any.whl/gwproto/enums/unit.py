from enum import auto
from typing import List

from fastapi_utils.enums import StrEnum


class Unit(StrEnum):
    """
    Specifies the physical unit of sensed data reported by SCADA

    Enum spaceheat.unit version 000 in the GridWorks Type registry.

    Used by used by multiple Application Shared Languages (ASLs), including but not limited to
    gwproto. For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#spaceheatunit)

    Values (with symbols in parens):
      - Unknown (00000000)
      - Unitless (ec972387)
      - W (f459a9c3)
      - Celcius (ec14bd47)
      - Fahrenheit (7d8832f8)
      - Gpm (b4580361)
      - WattHours (d66f1622)
      - AmpsRms (a969ac7c)
      - VoltsRms (e5d7555c)
      - Gallons (8e123a26)
    """

    Unknown = auto()
    Unitless = auto()
    W = auto()
    Celcius = auto()
    Fahrenheit = auto()
    Gpm = auto()
    WattHours = auto()
    AmpsRms = auto()
    VoltsRms = auto()
    Gallons = auto()

    @classmethod
    def default(cls) -> "Unit":
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
        The name in the GridWorks Type Registry (spaceheat.unit)
        """
        return "spaceheat.unit"

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
        Provides the encoding symbol for a Unit enum to send in seriliazed messages.

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
            "ec972387",
            "f459a9c3",
            "ec14bd47",
            "7d8832f8",
            "b4580361",
            "d66f1622",
            "a969ac7c",
            "e5d7555c",
            "8e123a26",
        ]


symbol_to_value = {
    "00000000": "Unknown",
    "ec972387": "Unitless",
    "f459a9c3": "W",
    "ec14bd47": "Celcius",
    "7d8832f8": "Fahrenheit",
    "b4580361": "Gpm",
    "d66f1622": "WattHours",
    "a969ac7c": "AmpsRms",
    "e5d7555c": "VoltsRms",
    "8e123a26": "Gallons",
}

value_to_symbol = {value: key for key, value in symbol_to_value.items()}

value_to_version = {
    "Unknown": "000",
    "Unitless": "000",
    "W": "000",
    "Celcius": "000",
    "Fahrenheit": "000",
    "Gpm": "000",
    "WattHours": "000",
    "AmpsRms": "000",
    "VoltsRms": "000",
    "Gallons": "000",
}
