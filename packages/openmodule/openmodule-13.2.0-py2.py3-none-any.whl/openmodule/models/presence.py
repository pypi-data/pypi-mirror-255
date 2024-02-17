from datetime import datetime
from typing import Optional, List

from pydantic import Field, root_validator

from openmodule.models.base import ZMQMessage, OpenModuleModel, Gateway, timezone_validator
from openmodule.models.vehicle import Medium, LPRMedium, MakeModel, PresenceAllIds, EnterDirection, QRMedium


class PresenceMedia(OpenModuleModel):
    lpr: Optional[LPRMedium]
    qr: Optional[QRMedium]
    nfc: Optional[Medium]
    pin: Optional[Medium]


class PresenceBaseData(OpenModuleModel):
    vehicle_id: int
    source: str
    present_area_name: str = Field(..., alias="present-area-name")
    last_update: datetime
    gateway: Gateway
    medium: PresenceMedia
    make_model: Optional[MakeModel]
    all_ids: PresenceAllIds
    enter_direction: EnterDirection = EnterDirection.unknown
    enter_time: datetime

    _tz_last_update = timezone_validator("last_update")
    _tz_enter_time = timezone_validator("enter_time")

    class Config:
        # allows setting attributes both via the alias, and the field name.
        # is used to rename old variables which are hard to understand by their name (e.g. id -> medium id)
        allow_population_by_field_name = True

    @root_validator(pre=True)
    def set_enter_time_default(cls, values):
        """for backward compatibility, set enter_time based on vehicle_id"""
        if values.get("enter_time") is None:
            values["enter_time"] = values["vehicle_id"] / 1e9  # timestamp from vehicle_id
        return values


class PresenceBaseMessage(PresenceBaseData, ZMQMessage):
    pass


class PresenceBackwardMessage(PresenceBaseMessage):
    type: str = "backward"
    unsure: bool = False
    leave_time: datetime = Field(..., alias="leave-time")
    bidirectional_inverse: bool = False

    _tz_leave_time = timezone_validator("leave_time")


class PresenceForwardMessage(PresenceBaseMessage):
    type: str = "forward"
    unsure: bool = False
    leave_time: datetime = Field(..., alias="leave-time")
    bidirectional_inverse: bool = False

    _tz_leave_time = timezone_validator("leave_time")


class PresenceLeaveMessage(PresenceBaseMessage):
    type: str = "leave"
    num_presents: int = Field(0, alias="num-presents")
    leave_time: datetime = Field(..., alias="leave-time")

    _tz_leave_time = timezone_validator("leave_time")

    @root_validator(pre=True)
    def set_leave_time_default(cls, values):
        if values.get("leave_time") is None:
            values["leave_time"] = values["timestamp"]  # timestamp from message timestamp
        return values


class PresenceEnterMessage(PresenceBaseMessage):
    type: str = "enter"


class PresenceChangeMessage(PresenceBaseMessage):
    type: str = "change"
    change_vehicle_id: Optional[bool]


class PresenceRPCRequest(OpenModuleModel):
    gate: str


class PresenceRPCResponse(OpenModuleModel):
    presents: List[PresenceBaseData]
