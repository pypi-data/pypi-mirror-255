"""Base for GridWorks gwproto gs.pwr.100 with TypeName p"""
import struct
from typing import List
from typing import NamedTuple

import gwproto.property_format as property_format


class GsPwrBase(NamedTuple):  #
    Power: int
    TypeName: str = "p"

    def as_type(self) -> bytes:
        return struct.pack("<h", self.Power)

    def derived_errors(self) -> List[str]:
        errors = []
        if self.TypeName != "p":
            errors.append(f"Payload requires TypeName of p, not {self.TypeName}.")
        if not isinstance(self.Power, int):
            errors.append(f"Name {self.Power} must have type int")
        if not property_format.is_short_integer(self.Power):
            errors.append(
                f"Power {self.Power} does not work. Short format requires (-32767 -1) <= number <= 32767"
            )
        return errors
