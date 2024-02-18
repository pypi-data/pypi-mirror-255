from typing import NamedTuple

from gwproto.data_classes.sh_node import ShNode
from gwproto.enums import TelemetryName


class TelemetryTuple(NamedTuple):
    AboutNode: ShNode
    SensorNode: ShNode
    TelemetryName: TelemetryName

    def __repr__(self):
        return f"TT({self.AboutNode.alias} {self.TelemetryName.value} read by {self.SensorNode.alias})"
