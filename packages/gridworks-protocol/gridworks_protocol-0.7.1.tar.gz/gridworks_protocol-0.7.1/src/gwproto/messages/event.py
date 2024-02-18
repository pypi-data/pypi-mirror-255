import time
import uuid
from enum import Enum
from typing import Any
from typing import Generic
from typing import Literal
from typing import Optional
from typing import TypeVar

from pydantic import BaseModel
from pydantic import Extra
from pydantic import Field
from pydantic import validator

from gwproto.message import Message
from gwproto.message import as_enum
from gwproto.types import GtShStatus
from gwproto.types import SnapshotSpaceheat


class EventBase(BaseModel):
    MessageId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    TimeNS: int = Field(default_factory=time.time_ns)
    Src: str = ""
    TypeName: str = Field(const=True)


class AnyEvent(EventBase, extra=Extra.allow):
    MessageId: str
    TimeNS: int
    Src: str
    TypeName: str


EventT = TypeVar("EventT", bound=EventBase)


class EventMessage(Message[EventT], Generic[EventT]):
    def __init__(self, **data: Any):
        if "AckRequired" not in data:
            data["AckRequired"] = True
        super().__init__(**data)


class StartupEvent(EventBase):
    TypeName: Literal["gridworks.event.startup"] = "gridworks.event.startup"


class ShutdownEvent(EventBase):
    Reason: str
    TypeName: Literal["gridworks.event.shutdown"] = "gridworks.event.shutdown"


class Problems(Enum):
    error = "error"
    warning = "warning"


class ProblemEvent(EventBase):
    ProblemType: Problems
    Summary: str
    Details: str = ""
    TypeName: Literal["gridworks.event.problem"] = "gridworks.event.problem"

    @validator("ProblemType", pre=True)
    def problem_type_value(cls, v: Any) -> Optional[Problems]:
        return as_enum(v, Problems, Problems.error)


class CommEvent(EventBase):
    PeerName: str


class MQTTCommEvent(CommEvent):
    ...


class MQTTConnectEvent(MQTTCommEvent):
    TypeName: Literal[
        "gridworks.event.comm.mqtt.connect"
    ] = "gridworks.event.comm.mqtt.connect"


class MQTTConnectFailedEvent(MQTTCommEvent):
    TypeName: Literal[
        "gridworks.event.comm.mqtt.connect.failed"
    ] = "gridworks.event.comm.mqtt.connect.failed"


class MQTTDisconnectEvent(MQTTCommEvent):
    TypeName: Literal[
        "gridworks.event.comm.mqtt.disconnect"
    ] = "gridworks.event.comm.mqtt.disconnect"


class MQTTFullySubscribedEvent(CommEvent):
    TypeName: Literal[
        "gridworks.event.comm.mqtt.fully.subscribed"
    ] = "gridworks.event.comm.mqtt.fully.subscribed"


class ResponseTimeoutEvent(CommEvent):
    TypeName: Literal[
        "gridworks.event.comm.response.timeout"
    ] = "gridworks.event.comm.response.timeout"


class PeerActiveEvent(CommEvent):
    TypeName: Literal[
        "gridworks.event.comm.peer.active"
    ] = "gridworks.event.comm.peer.active"


class GtShStatusEvent(EventBase):
    status: GtShStatus | dict
    TypeName: Literal["gridworks.event.gt.sh.status"] = "gridworks.event.gt.sh.status"


class SnapshotSpaceheatEvent(EventBase):
    snap: SnapshotSpaceheat | dict
    TypeName: Literal[
        "gridworks.event.snapshot.spaceheat"
    ] = "gridworks.event.snapshot.spaceheat"
