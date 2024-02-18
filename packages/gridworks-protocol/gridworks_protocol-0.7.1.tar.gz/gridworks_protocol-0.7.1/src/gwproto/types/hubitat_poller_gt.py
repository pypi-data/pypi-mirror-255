from pydantic import BaseModel
from pydantic import Extra
from pydantic import validator

from gwproto.enums import TelemetryName
from gwproto.enums import Unit
from gwproto.utils import snake_to_camel


class MakerAPIAttributeGt(BaseModel):
    attribute_name: str
    node_name: str
    telemetry_name_gt_enum_symbol: str = "c89d0ba1"
    unit_gt_enum_symbol: str = "ec14bd47"
    exponent: int = 3
    enabled: bool = True
    report_missing: bool = True
    report_parse_error: bool = True

    @property
    def telemetry_name(self) -> TelemetryName:
        value = TelemetryName.symbol_to_value(
            self.telemetry_name_gt_enum_symbol,
        )
        return TelemetryName(value)

    @property
    def unit(self) -> Unit:
        value = Unit.symbol_to_value(
            self.unit_gt_enum_symbol,
        )
        return Unit(value)

    class Config:
        extra = Extra.allow
        alias_generator = snake_to_camel
        allow_population_by_field_name = True

    @validator("telemetry_name_gt_enum_symbol")
    def _check_telemetry_name_symbol(cls, v: str) -> str:
        if v not in TelemetryName.symbols():
            v = TelemetryName.value_to_symbol(TelemetryName.default())
        return v


class HubitatPollerGt(BaseModel):
    hubitat_component_id: str
    device_id: int
    attributes: list[MakerAPIAttributeGt] = []
    enabled: bool = True
    poll_period_seconds: float = 60

    class Config:
        extra = Extra.allow
        alias_generator = snake_to_camel
        allow_population_by_field_name = True
