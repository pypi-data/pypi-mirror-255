from enum import Enum
from typing import List, Optional, Dict, Union

from pydantic import Field

from openmodule.models.base import OpenModuleModel, ZMQMessage, timezone_validator, CostEntryData
from openmodule.models.vehicle import Medium, LPRMedium, MakeModel

from dateutil import tz
from dateutil.parser import parse
from dateutil.rrule import rrulestr
from dateutil.tz import UTC
from pydantic import validator
import re
from datetime import datetime, tzinfo, timedelta


class AccessCategory(str, Enum):
    whitelist = "whitelist"                 # whitelist or other access services giving unrestricted free access
    booked = "booked"                       # anything already paid for (e.g. reservations)
    permanent = "permanent"                 # anything without parking costs except two cases above
    shortterm = "shortterm"                 # accesses with parking costs
    unknown = "unknown"                     # no access at all (unregistered shortterm parker)


class AccessRequestVehicle(OpenModuleModel):
    """
    The AccessRequestVehicle Model, represents all data sent by the controller,
     each backend should implement its own version to avoid problems when unnecessary fields change
    """
    lpr: Optional[LPRMedium]
    qr: Optional[Medium]
    pin: Optional[Medium]
    nfc: Optional[Medium]
    make_model: Optional[MakeModel]


class AccessCheckRequest(OpenModuleModel):
    """
    The AccessRequest Model
    """
    name: str                                                               # Name of the target Access Service
    gate: Optional[str] = None                                              # None means any gate
    vehicle: AccessRequestVehicle                                           # vehicle
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())  # check if access valid at this time

    _tz_timestamp = timezone_validator("timestamp")

    class Config:
        # allows setting attributes both via the alias, and the field name.
        # is used to rename old variables which are hard to understand by their name (e.g. id -> medium id)
        allow_population_by_field_name = True


class AccessCheckResponseError(str, Enum):
    offline = "offline"                     # access_service offline / connection error
    error = "error"                         # internal error


class AccessCheckRejectReason(str, Enum):  # see DEV-A-916
    wrong_gate = "wrong_gate"
    wrong_time = "wrong_time"
    anti_passback = "anti_passback"
    group_full = "group_full"
    limit_reached = "limit_reached"
    custom = "custom"


class AccessCheckAccess(OpenModuleModel):
    id: str                            # id of the access
    group_id: Optional[str]            # id for group-passback, in Digimon Contract ID, optional for 3rd Party Backends
    group_limit: Optional[int]         # limit for group-passback. None for unlimited
    customer_id: Optional[str]         # in Digimon Customer ID, optional for 3rd Party Backends
    car_id: Optional[str]              # in Digimon Customer Car ID, optional for 3rd Party Backends
    source: str                        # Access Service providing the access
    access_infos: Dict                 # Infos, which are added everywhere for later usage
    parksettings_id: Optional[str]     # None is no cost entries and access at any gate
    clearing: Optional[str]            # Clearing
    category: AccessCategory           # category used for sorting and eventlog
    media: Dict                        # media of the Access, e.g. {"lpr": "G ARIVO 1", "qr": "QR1"}
    used_medium: Medium                # medium in media which matched
    access_data: Dict                  # complete access data, will be used only for display and debug purposes

    accepted: bool                     # if access service decided access can enter
    reject_reason: Optional[AccessCheckRejectReason]  # only if not accepted: reason for not accepted
    decision_info: Optional[str]       # info for the decision (mainly for reject_reason "custom" or warnings)


class AccessCheckResponse(OpenModuleModel):
    success: bool
    error: Optional[AccessCheckResponseError]  # if successfully processed, offline or another error
    accesses: List[AccessCheckAccess] = []     # list of all matched accesses (including already rejected ones)


# The following messages are just for 3rd party backends which have their own session management
class BaseSessionMessage(ZMQMessage):
    id: str
    access_id: Optional[str] = Field(None, alias="user_id")
    access_infos: Optional[dict]
    group_id: Optional[str]
    customer_id: Optional[str]
    car_id: Optional[str]
    parking_area_id: Optional[str]

    class Config:
        # allows setting attributes both via the alias, and the field name.
        # is used to rename old variables which are hard to understand by their name (e.g. id -> medium id)
        allow_population_by_field_name = True

    @property
    def timestamp(self):
        raise NotImplementedError


class SessionStartMessage(BaseSessionMessage):
    type: str = "start"

    cost_table: dict

    entry_time: datetime
    entry_data: Dict

    _tz_entry_time = timezone_validator("entry_time")

    @property
    def timestamp(self):
        return self.entry_time


class SessionFinishMessage(BaseSessionMessage):
    type: str = "finish"

    entry_time: datetime
    entry_data: Dict
    exit_time: datetime
    exit_data: Dict

    _tz_entry_time = timezone_validator("entry_time")
    _tz_exit_time = timezone_validator("exit_time")

    @property
    def timestamp(self):
        return self.exit_time


class SessionDeleteMessage(BaseSessionMessage):
    type: str = "delete"

    reason: str
    delete_time: datetime

    entry_time: Optional[datetime]
    entry_data: Optional[Dict]
    exit_time: Optional[datetime]
    exit_data: Optional[Dict]

    _tz_delete_time = timezone_validator("delete_time")
    _tz_entry_time = timezone_validator("entry_time")
    _tz_exit_time = timezone_validator("exit_time")

    @property
    def timestamp(self):
        return self.delete_time


class SessionExitWithoutEntryMessage(BaseSessionMessage):
    type: str = "exit_without_entry"

    exit_time: datetime
    exit_data: Dict

    _tz_exit_time = timezone_validator("exit_time")

    @property
    def timestamp(self):
        return self.exit_time


# Double entry of vehicle
class SessionIncompleteMessage(BaseSessionMessage):
    type: str = "incomplete"

    related_session_id: str  # id of newly created session which caused the double entry

    entry_time: datetime
    entry_data: Dict

    _tz_entry_time = timezone_validator("entry_time")

    @property
    def timestamp(self):
        return self.entry_time


def check_recurrence(cls, recurrence, values, **kwargs):
    if recurrence:
        if not values.get("duration"):
            raise ValueError("set a duration when using recurrence")

        try:
            if "DTSTART" not in recurrence:
                raise ValueError("recurrence must contain a DTSTART field")
            if "\n" not in recurrence:
                raise ValueError("DTSTART must be separated by a newline '\\n' character")

            rrulestr(recurrence)
        except Exception as e:
            raise ValueError(f"recurrence is not valid '{e}'") from None
        return recurrence
    else:
        return None


class AccessTime(OpenModuleModel):
    start: Optional[datetime]
    end: Optional[datetime]
    duration: Optional[int]
    recurrence: Optional[str]

    _tz_start = timezone_validator("start")
    _tz_end = timezone_validator("end")

    _rrule_regex = re.compile(r"\s*DTSTART[:|=]+([\d\w+:]*)\s*[\n|;]*", re.IGNORECASE)
    _check_recurrence = validator("recurrence", allow_reuse=True)(check_recurrence)

    def _recurrence_is_valid_at(self, native_utc_dt: datetime, timezone):
        if isinstance(timezone, str):
            timezone = tz.gettz(timezone)

        # we first construct a rrule object with dtstart as a naive localized datetime
        dtstart_string = self._rrule_regex.search(self.recurrence).group(1)
        dtstart_utc = parse(dtstart_string).replace(tzinfo=UTC)
        local_dtstart = dtstart_utc.astimezone(timezone)
        naive_dtstart = local_dtstart.replace(tzinfo=None)
        recurrence_without_dtstart = self._rrule_regex.sub("", self.recurrence)
        recurrence = rrulestr(recurrence_without_dtstart, dtstart=naive_dtstart, cache=True)

        # get the nearest event before our desired timestamp
        local_dt = native_utc_dt.replace(tzinfo=UTC).astimezone(timezone)
        naive_dt = local_dt.replace(tzinfo=None)
        naive_before = recurrence.before(naive_dt, inc=True)
        if not naive_before:
            return False

        # calculate the start/end of the recurrent event
        local_before = naive_before.replace(tzinfo=timezone)
        local_after = local_before + timedelta(seconds=self.duration)

        # in case the utc offset jumps (dst change) we always add the time difference here, because there are two
        # groups of users, and we want to work for both
        # given a dst change at 03:00 back to 02:00:
        # a) user A always arrives at 02:00, and stays 2 hours, he does not care if a dst change happened, he always
        #    stays 2 hours, regardless of the dst change, for him `start + timedelta(hours=2)` would work
        # b) user B always arrives at 04:00, so he does not care that there has been an extra hour between 2 and 4
        # o'clock, he arrives at 04:00. For hom `start + timedelta(hours=2)` would miss by an hour
        utc_offset_diff = abs(local_before.utcoffset() - local_after.utcoffset())
        if utc_offset_diff.total_seconds() != 0:
            local_after += utc_offset_diff
        naive_after = local_after.replace(tzinfo=None)

        return naive_before <= naive_dt < naive_after

    def is_valid_at(self, dt: datetime, timezone: Union[str, tzinfo]):
        if dt.tzinfo:
            dt = dt.astimezone(UTC).replace(tzinfo=None)

        if self.start and self.end:
            between_start_and_end = self.start <= dt <= self.end
        elif self.start:
            between_start_and_end = self.start <= dt
        elif self.end:
            between_start_and_end = dt <= self.end
        else:
            between_start_and_end = True

        if self.recurrence:
            return between_start_and_end and self._recurrence_is_valid_at(dt, timezone)
        else:
            return between_start_and_end
