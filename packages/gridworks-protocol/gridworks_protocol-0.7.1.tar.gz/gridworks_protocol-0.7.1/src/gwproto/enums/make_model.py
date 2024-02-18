from enum import auto
from typing import List

from fastapi_utils.enums import StrEnum


class MakeModel(StrEnum):
    """
    Determines Make/Model of device associated to a Spaceheat Node supervised by SCADA

    Enum spaceheat.make.model version 001 in the GridWorks Type registry.

    Used by used by multiple Application Shared Languages (ASLs), including but not limited to
    gwproto. For more information:
      - [ASLs](https://gridworks-type-registry.readthedocs.io/en/latest/)
      - [Global Authority](https://gridworks-type-registry.readthedocs.io/en/latest/enums.html#spaceheatmakemodel)
      - [More Info](https://gridworks-protocol.readthedocs.io/en/latest/make-model.html)

    Values (with symbols in parens):
      - UnknownMake__UnknownModel (00000000)
      - Egauge__4030 (beb6d3fb): A power meter in Egauge's 403x line. [More Info](https://drive.google.com/drive/u/0/folders/1abJ-o9tlTscsQpMvT6SHxIm5j5aODgfA).
      - NCD__PR8-14-SPST (fabfa505): NCD's 4-channel high-power relay controller + 4 GPIO with I2C
        interface. [More Info](https://store.ncd.io/product/4-channel-high-power-relay-controller-4-gpio-with-i2c-interface/?attribute_pa_choose-a-relay=20-amp-spdt).
      - Adafruit__642 (acd93fb3): Adafruit's high-temp, water-proof 1-wire temp sensor. [More Info](https://www.adafruit.com/product/642).
      - GridWorks__TSnap1 (d0178dc3): Actual GridWorks TSnap 1.0 SCADA Box.
      - GridWorks__WaterTempHighPrecision (f8b497e8): Simulated temp sensor.
      - Gridworks__SimPm1 (076da322): Simulated power meter.
      - SchneiderElectric__Iem3455 (d300635e): Schneider Electric IEM 344 utility meter.
      - GridWorks__SimBool30AmpRelay (e81d74a8): Simulated relay.
      - OpenEnergy__EmonPi (c75d269f): Open Energy's open source multipurpose sensing device (including
        internal power meter). [More Info](https://docs.openenergymonitor.org/emonpi/technical.html).
      - GridWorks__SimTSnap1 (3042c432): Simulated SCADA Box.
      - Atlas__EzFlo (d0b0e375): Atlas Scientific EZO Embedded Flow Meter Totalizer, pulse to I2C. [More Info](https://drive.google.com/drive/u/0/folders/142bBV1pQIbMpyIR_0iRUr5gnzWgknOJp).
      - Hubitat__C7__LAN1 (4d649420): This refers to a Hubitat C7 that has been configured in a specific
        way with respect to the APIs it presents on the Local Area Network. The Hubitat C7 is
        a home automation hub that supports building ZigBee and ZWave meshes, plugs into Ethernet,
        has a reasonable user interface and has an active community of open-source developers
        who create drivers and package managers for devices, and supports the creation of various
        types of APIs on the Local Area Network. [More Info](https://drive.google.com/drive/folders/1AqAU_lC2phzuI9XRYvogiIYA7GXNtlr6).
      - GridWorks__Tank_Module_1 (bd759051): This refers to a small module designed and assembled
        by GridWorks that is meant to be mounted to the side of a hot water tank. It requires
        24V DC and has 4 temperature sensors coming out of it labeled 1, 2, 3 and 4. It is meant
        to provide temperature readings (taken within a half a second of each other) of all
        4 of its sensors once a minute. [More Info](https://drive.google.com/drive/folders/1GSxDd8Naf1GKK_fSOgQU933M1UcJ4r8q).
      - Fibaro__Analog_Temp_Sensor (1f19839d): This enum refers to a Fibaro FGBS-222 home automation
        device that has been configured in a specific way. This includes (1) being attached
        to two 10K NTC thermistors and a specific voltage divider circuit that specifies its
        temperature as a function of voltage and (2) one of its potential free outputs being
        in-line with the power of a partner Fibaro, so that it can power cycle its partner (because
        there are reports of Fibaros no longer reporting temp change after weeks or months until
        power cylced). The Fibaro itself is a tiny (29 X 18 X 13 mm) Z-Wave device powered on
        9-30V DC that can read up to 6 1-wire DS18B20 temp sensors, 2 0-10V analog inputs and
        also has 2 potential free outputs. [More Info](https://drive.google.com/drive/u/0/folders/1Muhsvw00goppHIfGSEmreX4hM6V78b-m).
      - Amphenol__NTC_10K_Thermistor_MA100GG103BN (46f21cd5): A small gauge, low-cost, rapid response
        NTC 10K Thermistor designed for medical applications. [More Info](https://drive.google.com/drive/u/0/folders/11HW4ov66UvxKAwqApW6IrtoXatZBLQkd).
      - YHDC__SCT013-100 (08da3f7d): YHDC current transformer [More Info](https://en.yhdc.com/product/SCT013-401.html).
      - Magnelab__SCT-0300-050 (a8d9a70d): Magnelab 50A current transformer
      - GridWorks__MultiTemp1 (bb31d136): GridWorks Analog temperature sensor that has 12 channels
        (labeled 1-12) to read 12 10K NTC Thermistors. It is comprised of 3 NCD ADS 1115 I2C
        temperature sensors with I2C Addresses 0x4b, 0x48, 0x49. [More Info](https://drive.google.com/drive/u/0/folders/1OuY0tunaad2Ie4Id3zFB7FcbEwHizWuL).
      - Krida__Emr16-I2c-V3 (3353ce46): 16-Channel I2C Low Voltage Electromagnetic Relay Board [More Info](https://drive.google.com/drive/u/0/folders/1jL82MTRKEh9DDmxJFQ2yU2cjqnVD9Ik7).
    """

    UNKNOWNMAKE__UNKNOWNMODEL = auto()
    EGAUGE__4030 = auto()
    NCD__PR814SPST = auto()
    ADAFRUIT__642 = auto()
    GRIDWORKS__TSNAP1 = auto()
    GRIDWORKS__WATERTEMPHIGHPRECISION = auto()
    GRIDWORKS__SIMPM1 = auto()
    SCHNEIDERELECTRIC__IEM3455 = auto()
    GRIDWORKS__SIMBOOL30AMPRELAY = auto()
    OPENENERGY__EMONPI = auto()
    GRIDWORKS__SIMTSNAP1 = auto()
    ATLAS__EZFLO = auto()
    HUBITAT__C7__LAN1 = auto()
    GRIDWORKS__TANK_MODULE_1 = auto()
    FIBARO__ANALOG_TEMP_SENSOR = auto()
    AMPHENOL__NTC_10K_THERMISTOR_MA100GG103BN = auto()
    YHDC__SCT013100 = auto()
    MAGNELAB__SCT0300050 = auto()
    GRIDWORKS__MULTITEMP1 = auto()
    KRIDA__EMR16I2CV3 = auto()

    @classmethod
    def default(cls) -> "MakeModel":
        """
        Returns default value (in this case UNKNOWNMAKE__UNKNOWNMODEL)
        """
        return cls.UNKNOWNMAKE__UNKNOWNMODEL

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
        The name in the GridWorks Type Registry (spaceheat.make.model)
        """
        return "spaceheat.make.model"

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
            a later version of this enum, returns the default value of "UnknownMake__UnknownModel".
        """
        if symbol not in symbol_to_value.keys():
            return cls.default().value
        return symbol_to_value[symbol]

    @classmethod
    def value_to_symbol(cls, value: str) -> str:
        """
        Provides the encoding symbol for a MakeModel enum to send in seriliazed messages.

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
            "beb6d3fb",
            "fabfa505",
            "acd93fb3",
            "d0178dc3",
            "f8b497e8",
            "076da322",
            "d300635e",
            "e81d74a8",
            "c75d269f",
            "3042c432",
            "d0b0e375",
            "4d649420",
            "bd759051",
            "1f19839d",
            "46f21cd5",
            "08da3f7d",
            "a8d9a70d",
            "bb31d136",
            "3353ce46",
        ]


symbol_to_value = {
    "00000000": "UNKNOWNMAKE__UNKNOWNMODEL",
    "beb6d3fb": "EGAUGE__4030",
    "fabfa505": "NCD__PR814SPST",
    "acd93fb3": "ADAFRUIT__642",
    "d0178dc3": "GRIDWORKS__TSNAP1",
    "f8b497e8": "GRIDWORKS__WATERTEMPHIGHPRECISION",
    "076da322": "GRIDWORKS__SIMPM1",
    "d300635e": "SCHNEIDERELECTRIC__IEM3455",
    "e81d74a8": "GRIDWORKS__SIMBOOL30AMPRELAY",
    "c75d269f": "OPENENERGY__EMONPI",
    "3042c432": "GRIDWORKS__SIMTSNAP1",
    "d0b0e375": "ATLAS__EZFLO",
    "4d649420": "HUBITAT__C7__LAN1",
    "bd759051": "GRIDWORKS__TANK_MODULE_1",
    "1f19839d": "FIBARO__ANALOG_TEMP_SENSOR",
    "46f21cd5": "AMPHENOL__NTC_10K_THERMISTOR_MA100GG103BN",
    "08da3f7d": "YHDC__SCT013100",
    "a8d9a70d": "MAGNELAB__SCT0300050",
    "bb31d136": "GRIDWORKS__MULTITEMP1",
    "3353ce46": "KRIDA__EMR16I2CV3",
}

value_to_symbol = {value: key for key, value in symbol_to_value.items()}

value_to_version = {
    "UNKNOWNMAKE__UNKNOWNMODEL": "000",
    "EGAUGE__4030": "000",
    "NCD__PR814SPST": "000",
    "ADAFRUIT__642": "000",
    "GRIDWORKS__TSNAP1": "000",
    "GRIDWORKS__WATERTEMPHIGHPRECISION": "000",
    "GRIDWORKS__SIMPM1": "000",
    "SCHNEIDERELECTRIC__IEM3455": "000",
    "GRIDWORKS__SIMBOOL30AMPRELAY": "000",
    "OPENENERGY__EMONPI": "000",
    "GRIDWORKS__SIMTSNAP1": "000",
    "ATLAS__EZFLO": "000",
    "HUBITAT__C7__LAN1": "001",
    "GRIDWORKS__TANK_MODULE_1": "001",
    "FIBARO__ANALOG_TEMP_SENSOR": "001",
    "AMPHENOL__NTC_10K_THERMISTOR_MA100GG103BN": "001",
    "YHDC__SCT013100": "001",
    "MAGNELAB__SCT0300050": "001",
    "GRIDWORKS__MULTITEMP1": "001",
    "KRIDA__EMR16I2CV3": "001",
}
