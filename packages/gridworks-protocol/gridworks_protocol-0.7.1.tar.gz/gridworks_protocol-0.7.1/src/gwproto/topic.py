import dataclasses
from dataclasses import dataclass


@dataclass
class DecodedMQTTTopic:
    envelope_type: str = ""
    src: str = ""
    message_type: str = ""
    remainder: list[str] = dataclasses.field(default_factory=list)

    def __str__(self) -> str:
        return f"DecodedMQTTTopic {self.envelope_type}/{self.src}/{self.message_type} remainder:{self.remainder}"


class MQTTTopic:
    """Valid Gridworks MQTT topic is one of:

     - ENVELOPE_TYPE/SRC/MESSAGE_TYPE, for example: 'gw/hw1-isone-ma-boston-scada/snapshot-spaceheat',
        meaning a message using envelope format 'gw', from 'hw1-isone-ma-boston-scada', with message type
        'snapshot-spaceheat'.

     - ENVELOPE_TYPE/src, for exxample: 'gw/hw1-isone-ma-boston-scada',
        meaning a message using envelope format 'gw', from 'hw1-isone-ma-boston-scada'. Message type must be inferred
        the contents of the envelope.

    - ENVELOPE_TYPE, for example: 'gw',
        meaning a message using envelope format 'gw'. Source and message type must be inferred the contents of the
        envelope.

     - ENVELOPE_TYPE/SRC/MESSAGE_TYPE/OTHER/STUFF, for example: 'gw/hw1-isone-ma-boston-scada/snapshot-spaceheat/bla/bla',
        meaning a message using envelope format 'gw', from 'hw1-isone-ma-boston-scada', with message type
        'snapshot-spaceheat', with extra components OTHER and STUFF that may be used by code down-stream code.

    The only valid component separator is '/'.

    '.' is not a valid character inside the mqtt topic. It must be replaced with '-'.

    It is an error for the message type contained inside the envelope to differ from one specified in the topic.
    """

    DOT_REPLACEMENT = "-"
    SEPARATOR = "/"

    @classmethod
    def encode(cls, envelope_type: str, src: str, message_type: str) -> str:
        return (
            envelope_type + cls.SEPARATOR + src + cls.SEPARATOR + message_type
        ).replace(".", cls.DOT_REPLACEMENT)

    @classmethod
    def encode_subscription(cls, envelope_type: str, src: str) -> str:
        return cls.encode(envelope_type, src, "#")

    @classmethod
    def decode(cls, topic: str) -> DecodedMQTTTopic:
        if not topic:
            raise ValueError("ERROR. Topic must have at least one character")
        topic = str(topic).replace("-", ".")
        split = topic.split(cls.SEPARATOR)
        if len(split) == 1:
            envelope_type = split[0]
            src = ""
            message_type = ""
        elif len(split) == 2:
            envelope_type = split[0]
            src = split[1]
            message_type = ""
        else:
            envelope_type = split[0]
            src = split[1]
            message_type = split[2]
        return DecodedMQTTTopic(
            envelope_type=envelope_type,
            src=src,
            message_type=message_type,
            remainder=split[3:],
        )
