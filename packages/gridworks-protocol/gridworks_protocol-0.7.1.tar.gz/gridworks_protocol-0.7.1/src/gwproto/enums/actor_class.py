from enum import auto
from typing import List

from fastapi_utils.enums import StrEnum


class ActorClass(StrEnum):
    """
    Determines the code running Spaceheat Nodes supervised by Spaceheat SCADA software

    Enum sh.actor.class version 001 in the GridWorks Type registry.

    Used by used by multiple Application Shared Languages (ASLs), including but not limited to
    gwproto. For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#shactorclass)
      - [More Info](https://gridworks-protocol.readthedocs.io/en/latest/actor-class.html)

    Values (with symbols in parens):
      - NoActor (00000000): A SpaceheatNode that does not have any code running on its behalf within
        the SCADA, but is instead only a reference object (for example, a tank of hot water
        or a resistive element) that can be discussed (for example, the power drawn by the resistive
        element can be measured) or evaluated (for example, a set of 5 different temperatures
        in different places on the tank can be used to estimate total thermal energy in the
        tank).
      - Scada (6d37aa41): The SCADA actor is the prime piece of code running and supervising other
        ProActors within the SCADA code. It is also responsible for managing the state of TalkingWith
        the AtomicTNode, as well maintaining and reporting a boolean state variable that indicates
        whether it is following dispatch commands from the AtomicTNode XOR following dispatch
        commands from its own HomeAlone actor.
      - HomeAlone (32d3d19f): HomeAlone is an abstract Spaceheat Actor responsible for dispatching
        the SCADA when it is not talking with the AtomicTNode.
      - BooleanActuator (fddd0064): A SpaceheatNode representing a generic boolean actuator capable
        of turning on (closing a circuit) or turning off (opening a circuit).
      - PowerMeter (2ea112b9): A SpaceheatNode representing the power meter that is used to settle
        financial transactions with the TerminalAsset. That is, this is the power meter whose
        accuracy is certified in the creation of the TerminalAsset GNode via creation of the
        TaDeed. [More Info](https://gridworks.readthedocs.io/en/latest/terminal-asset.html).
      - Atn (b103058f): A SpaceheatNode representing the AtomicTNode. Note that the code running
        the AtomicTNode is not local within the SCADA code, except for a stub used for testing
        purposes. [More Info](https://gridworks.readthedocs.io/en/latest/atomic-t-node.html).
      - SimpleSensor (dae4b2f0): A SpaceheatNode representing a sensor that measures a single category
        of quantity (for example, temperature) for a single object (for example, on a pipe). [More Info](https://gridworks-protocol.readthedocs.io/en/latest/simple-sensor.html).
      - MultipurposeSensor (7c483ad0): A sensor that either reads multiple kinds of readings from
        the same sensing device (for example reads current and voltage), reads multiple different
        objects (temperature from two different thermisters) or both. [More Info](https://gridworks-protocol.readthedocs.io/en/latest/multipurpose-sensor.html).
      - Thermostat (4a9c1785): A SpaceheatNode representing a thermostat.
      - HubitatTelemetryReader (0401b27e): A generic actor for reading telemetry data from a Hubitat
        Home Automation Hub LAN API. [More Info](https://drive.google.com/drive/u/0/folders/1AqAU_lC2phzuI9XRYvogiIYA7GXNtlr6).
      - HubitatTankModule (e2877329): The actor for running a GridWorks TankModule, comprised of
        two Z-Wave Fibaro temp sensors built together inside a small container that has 4 thermistors
        attached. These are designed to be installed from top (1) to bottom (4) on a stratified
        thermal storage tank. [More Info](https://drive.google.com/drive/u/0/folders/1GSxDd8Naf1GKK_fSOgQU933M1UcJ4r8q).
      - HubitatPoller (00000100): An actor for representing a somewhat generic ShNode (like a thermostat)
        that can be polled through the Hubitat.
    """

    NoActor = auto()
    Scada = auto()
    HomeAlone = auto()
    BooleanActuator = auto()
    PowerMeter = auto()
    Atn = auto()
    SimpleSensor = auto()
    MultipurposeSensor = auto()
    Thermostat = auto()
    HubitatTelemetryReader = auto()
    HubitatTankModule = auto()
    HubitatPoller = auto()

    @classmethod
    def default(cls) -> "ActorClass":
        """
        Returns default value (in this case NoActor)
        """
        return cls.NoActor

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
        The name in the GridWorks Type Registry (sh.actor.class)
        """
        return "sh.actor.class"

    @classmethod
    def enum_version(cls) -> str:
        """
        The version in the GridWorks Type Registry (001)
        """
        return "001"

    @classmethod
    def symbol_to_value(cls, symbol: str) -> str:
        """
        Given the symbol sent in a serialized message, returns the encoded enum.

        Args:
            symbol (str): The candidate symbol.

        Returns:
            str: The encoded value associated to that symbol. If the symbol is not
            recognized - which could happen if the actor making the symbol is using
            a later version of this enum, returns the default value of "NoActor".
        """
        if symbol not in symbol_to_value.keys():
            return cls.default().value
        return symbol_to_value[symbol]

    @classmethod
    def value_to_symbol(cls, value: str) -> str:
        """
        Provides the encoding symbol for a ActorClass enum to send in seriliazed messages.

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
            "6d37aa41",
            "32d3d19f",
            "fddd0064",
            "2ea112b9",
            "b103058f",
            "dae4b2f0",
            "7c483ad0",
            "4a9c1785",
            "0401b27e",
            "e2877329",
            "00000100",
        ]


symbol_to_value = {
    "00000000": "NoActor",
    "6d37aa41": "Scada",
    "32d3d19f": "HomeAlone",
    "fddd0064": "BooleanActuator",
    "2ea112b9": "PowerMeter",
    "b103058f": "Atn",
    "dae4b2f0": "SimpleSensor",
    "7c483ad0": "MultipurposeSensor",
    "4a9c1785": "Thermostat",
    "0401b27e": "HubitatTelemetryReader",
    "e2877329": "HubitatTankModule",
    "00000100": "HubitatPoller",
}

value_to_symbol = {value: key for key, value in symbol_to_value.items()}

value_to_version = {
    "NoActor": "000",
    "Scada": "000",
    "HomeAlone": "000",
    "BooleanActuator": "000",
    "PowerMeter": "000",
    "Atn": "000",
    "SimpleSensor": "000",
    "MultipurposeSensor": "000",
    "Thermostat": "000",
    "HubitatTelemetryReader": "001",
    "HubitatTankModule": "001",
    "HubitatPoller": "001",
}
