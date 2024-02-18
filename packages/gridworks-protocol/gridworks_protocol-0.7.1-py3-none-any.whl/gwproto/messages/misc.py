import uuid
from typing import Any
from typing import Literal

from pydantic import BaseModel
from pydantic import Field

from gwproto.message import Message


class Ack(BaseModel):
    AckMessageID: str
    TypeName: Literal["gridworks.ack"] = "gridworks.ack"


class Ping(BaseModel):
    MessageId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    TypeName: Literal["gridworks.ping"] = "gridworks.ping"


class PingMessage(Message[Ping]):
    def __init__(self, **data: Any):
        if "AckRequired" not in data:
            data["AckRequired"] = True
        if "Payload" not in data:
            data["Payload"] = Ping()
        super().__init__(**data)
