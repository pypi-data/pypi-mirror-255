import datetime
import json
import re
import subprocess
from typing import Any

import pytz


snake_add_underscore_to_camel_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def camel_to_snake(name: str) -> str:
    return snake_add_underscore_to_camel_pattern.sub("_", name).lower()


def snake_to_camel(word: str) -> str:
    return "".join(x.capitalize() or "_" for x in word.split("_"))


def string_to_dict(payload_as_string: str) -> dict[str, Any]:
    payload_as_dict = json.loads(payload_as_string)
    if not isinstance(payload_as_dict, dict):
        raise ValueError(
            f"ERROR. json.loads(payload) produced {type(payload_as_dict)} not dict"
        )
    return payload_as_dict


def log_style_utc_date(timestamp: float) -> str:
    d = datetime.datetime.utcfromtimestamp(timestamp)
    d = pytz.UTC.localize(d)
    utc_date = d.strftime("%Y-%m-%d %H:%M:%S")
    return utc_date + d.strftime(" %Z")


def log_style_utc_date_w_millis(timestamp: float) -> str:
    d = datetime.datetime.utcfromtimestamp(timestamp)
    d = pytz.UTC.localize(d)
    millis = round(d.microsecond / 1000)
    if millis == 1000:
        d += datetime.timedelta(seconds=1)
        millis = 0
    utc_date = d.strftime("%Y-%m-%d %H:%M:%S")
    if 0 <= millis < 10:
        millis_string = f".00{millis}"
    elif 10 <= millis < 100:
        millis_string = f".0{millis}"
    else:
        millis_string = f".{millis}"
    return utc_date + millis_string + d.strftime(" %Z")


def screen_style_utc_date_w_millis(timestamp: float) -> str:
    d = datetime.datetime.utcfromtimestamp(timestamp)
    d = pytz.UTC.localize(d)
    millis = round(d.microsecond / 1000)
    utc_date = d.strftime("%M:%S")
    if 0 <= millis < 10:
        millis_string = f".00{millis}"
    elif 10 <= millis < 100:
        millis_string = f".0{millis}"
    else:
        millis_string = f".{millis}"
    return utc_date + millis_string


def screen_style_utc_date_s(timestamp: float) -> str:
    d = datetime.datetime.utcfromtimestamp(timestamp)
    d = pytz.UTC.localize(d)
    utc_date = d.strftime("%Y-%m-%d %H:%M:%S")
    return utc_date + " UTC"


def get_git_short_commit() -> str:
    return bytes.decode(
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
    ).split("\n")[0]


def rld_alias(alias: str) -> str:
    return ".".join(reversed(alias.split(".")))


def all_equal(iterator: Any) -> bool:
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == x for x in iterator)


# def predicate_validator(
#     field_name: str, predicate: Callable[[Any], bool], error_format: str = "", **kwargs
# ) -> classmethod:  # type: ignore

MAC_REGEX = re.compile("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$")


def has_mac_address_format(mac_str: str) -> bool:
    return bool(MAC_REGEX.match(mac_str.lower()))
