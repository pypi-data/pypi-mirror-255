import base64
import binascii
import re
from datetime import datetime
from decimal import Decimal
from enum import Enum
from json.encoder import ESCAPE_ASCII
from typing import Optional, Union

import orjson
import zmq
from dateutil.tz import UTC
from pydantic import Field, BaseModel, validator, root_validator
from pydantic.main import ROOT_KEY

from openmodule import config
from openmodule.config import settings


def _donotuse(v, *, default):
    assert False, "please use json_bytes"


if config.run_checks():
    from openmodule import checks

    meta_kwargs = {"metaclass": checks.CheckingOpenModuleModel}
else:
    meta_kwargs = {}

ESCAPE_ASCII = re.compile(r'([^ -~])')


def replace(match):
    s = match.group(0)
    n = ord(s)
    if n < 0x10000:
        return '\\u%04x' % (n,)
    else:
        # surrogate pair
        n -= 0x10000
        s1 = 0xd800 | ((n >> 10) & 0x3ff)
        s2 = 0xdc00 | (n & 0x3ff)
        return '\\u%04x\\u%04x' % (s1, s2)


def _unicode_escape(data):
    return ESCAPE_ASCII.sub(replace, data)


def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    if settings.TESTING:
        from freezegun.api import FakeDatetime
        if isinstance(obj, FakeDatetime):
            return obj.isoformat()
    raise TypeError


class OpenModuleModel(BaseModel, **meta_kwargs):
    class Config:
        validate_assignment = True

        json_loads = orjson.loads
        json_dumps = _donotuse

    def json_bytes(self):
        data = self.dict()
        if self.__custom_root_type__:
            data = data[ROOT_KEY]
        return _unicode_escape(orjson.dumps(data, default=default).decode()).encode("ascii")

    def dict(self, **kwargs):
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", True)
        return super().dict(**kwargs)


class EmptyModel(OpenModuleModel):
    pass


def _timezone_validator(cls, dt: datetime, values, **kwargs):
    if dt and dt.tzinfo:
        return dt.astimezone(UTC).replace(tzinfo=None)
    else:
        return dt


def timezone_validator(field):
    return validator(field, allow_reuse=True)(_timezone_validator)


def _base64_validator(cls, data, values, **kwargs):
    try:
        base64.b64decode(data)
    except (binascii.Error, TypeError, ValueError):
        raise ValueError("must be a base64 string")
    return data


def base64_validator(field):
    return validator(field, allow_reuse=True)(_base64_validator)


_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=UTC)
_EPOCH_NAIVE = datetime(1970, 1, 1)


def datetime_to_timestamp(dt: datetime):
    """
    you SHOULD use this function, as it always outputs the UTC unix timestamp, regardless
    of the system's timezone. This is not an issue in production as all systems run UTC,
    but while developing it creates annoying bugs
    """
    if dt.tzinfo is None:
        return (dt - _EPOCH_NAIVE).total_seconds()
    else:
        return (dt - _EPOCH_UTC).total_seconds()


class ZMQMessage(OpenModuleModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())
    name: str
    type: str

    def __init__(self, **kwargs):
        name = kwargs.pop("name", None)
        if name is None:
            name = settings.NAME
        super().__init__(name=name, **kwargs)

    _tz_timestamp = timezone_validator("timestamp")

    def publish_on_topic(self, pub_socket: zmq.Socket, topic: str):
        assert isinstance(topic, str), "topic must be a string"

        pub_socket.send_multipart((topic.encode("utf8"), self.json_bytes()))

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        data["timestamp"] = datetime_to_timestamp(data["timestamp"])
        return data


class Direction(str, Enum):
    UNKNOWN = ""
    IN = "in"
    OUT = "out"


class Gateway(OpenModuleModel):
    gate: str = ""
    direction: Direction = ""

    def __str__(self):
        return f"{self.gate}/{self.direction}"


class CostEntryData(OpenModuleModel):
    entry_type: str
    value: Optional[Union[int, str]]
    group: Optional[str]
    account_id: str
    source: Optional[str]  # if None, source will be set to service name on default: e.g. "service_iocontroller"
    source_id: Optional[str]
    idempotency_key: Optional[str]

    @root_validator
    def set_value_type(cls, values):
        if values["entry_type"] in ["rate_change", "rate_validation", "partial_rate_change"]:
            values["value"] = str(values["value"])
        elif values["entry_type"] in ["static_cost", "pending_static_cost", "amount_validation", "time_validation"
                                      "payment"]:
            values["value"] = int(values["value"])
        return values
