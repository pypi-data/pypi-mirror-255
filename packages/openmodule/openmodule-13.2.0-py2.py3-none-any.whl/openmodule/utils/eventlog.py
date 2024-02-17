import logging
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Union

from pydantic import validator, root_validator

from openmodule.core import core
from openmodule.models.base import OpenModuleModel, ZMQMessage, timezone_validator

log = logging.getLogger("Eventlog")


class AnonymizationType(str, Enum):
    lpr = "lpr"  # anonymize to "***AB"
    medium = "medium"  # anonymize if linked to a session
    default = "default"  # anonymize ":anonymize:" -> display with anonymize icon
    no = "no"


class PlateFormatData(OpenModuleModel):
    plate: str
    country: Optional[str]


class MessageKwarg(OpenModuleModel):
    value: Union[PlateFormatData, int, float, bool, str]
    anonymization_type: AnonymizationType = AnonymizationType.default
    format_type: str

    @staticmethod
    def lpr(plate: str, country: Optional[str] = None):
        return MessageKwarg(value=PlateFormatData(plate=plate, country=country or "-"), format_type="lpr",
                            anonymization_type=AnonymizationType.lpr)

    @staticmethod
    def medium(value: str):
        return MessageKwarg(value=value, format_type="medium", anonymization_type=AnonymizationType.medium)

    @staticmethod
    def string(value: str):
        return MessageKwarg(value=value, format_type="string", anonymization_type=AnonymizationType.default)

    @staticmethod
    def price(cents: int):
        return MessageKwarg(value=cents, format_type="price", anonymization_type=AnonymizationType.no)

    @staticmethod
    def rate(rate_id: str):
        return MessageKwarg(value=rate_id, format_type="rate", anonymization_type=AnonymizationType.no)

    @staticmethod
    def cost_group(cost_group: str):
        return MessageKwarg(value=cost_group, format_type="cost_group", anonymization_type=AnonymizationType.no)

    @staticmethod
    def gate(technical_name: str):
        return MessageKwarg(value=technical_name, format_type="gate", anonymization_type=AnonymizationType.no)

    @root_validator
    def check_value_type_to_format_type(cls, values):
        if values["format_type"] == "lpr":
            assert isinstance(values["value"], PlateFormatData), "lpr has to be PlateFormatData"
        if values["format_type"] == "medium":
            assert isinstance(values["value"], str), "medium has to be str"
        if values["format_type"] == "string":
            assert isinstance(values["value"], str), "string has to be str"
        if values["format_type"] == "price":
            assert isinstance(values["value"], int), "price has to be int"
        if values["format_type"] == "gate":
            assert isinstance(values["value"], str), "gate has to be str"
        return values


class EventInfo(OpenModuleModel):
    type: str  # a category for icons and grouping, must contain at least one "_", hierarchy via prefix
    timestamp: datetime
    gate: Optional[str]
    license_plate: Optional[str]  # anonymized with type lpr
    license_plate_country: Optional[str]
    session_id: Optional[str]
    related_session_id: Optional[str]
    vehicle_id: Optional[str]
    price: Optional[int]  # cents

    _tz_timestamp = timezone_validator("timestamp")

    @validator("type")
    def type_contains_underscore(cls, v):
        assert "_" in v, "type must container at least one underscore"
        return v

    @staticmethod
    def create(type: str, timestamp: Optional[datetime] = None, gate: Optional[str] = None,
               license_plate: Optional[str] = None, license_plate_country: Optional[str] = None,
               session_id: Optional[str] = None, related_session_id: Optional[str] = None,
               vehicle_id: Optional[str] = None, price: Optional[int] = None):
        return EventInfo(type=type, timestamp=timestamp or datetime.utcnow(), gate=gate, license_plate=license_plate,
                         license_plate_country=license_plate_country, session_id=session_id,
                         related_session_id=related_session_id, vehicle_id=vehicle_id, price=price)


class Event(OpenModuleModel):
    message: str  # e.g. 'Session with license plate {lpr} at entry "Einfahrt" started.'
    message_kwargs: Dict[str, MessageKwarg]  # e.g. {"lpr": }
    infos: EventInfo


class EventlogMessage(ZMQMessage):
    type = "create_event"
    event: Event

    def send(self):
        """publish the message with the core publisher on the eventlog topic"""
        core().publish(self, "eventlog")

    @staticmethod
    def create(infos: EventInfo, message: str, **message_kwargs: MessageKwarg):
        """create a new eventlog message with the given parameters"""
        return EventlogMessage(event=Event(infos=infos, message=message, message_kwargs=message_kwargs))


def send_event(infos: EventInfo, message: str, **message_kwargs: MessageKwarg):
    format_kwargs = {key: kwarg.value for key, kwarg in message_kwargs.items()}
    if infos.gate:
        log.info(f"Sending event at {infos.gate}: {message.format(**format_kwargs)}")
    else:
        log.info(f"Sending event: {message.format(**format_kwargs)}")
    EventlogMessage.create(infos=infos, message=message, **message_kwargs).send()
