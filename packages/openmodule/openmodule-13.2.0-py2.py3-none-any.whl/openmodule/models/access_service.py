from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict

from pydantic import Field, root_validator

from openmodule.models.base import OpenModuleModel, timezone_validator
from openmodule.models.vehicle import Medium, LPRMedium, MakeModel


class AccessCategory(str, Enum):
    handauf = "handauf"                     # handauf qr codes
    whitelist = "whitelist"                 # whitelist or other access services giving unrestricted free access
    booked = "booked"                       # anything already paid for (e.g. reservations)
    permanent = "permanent"                 # anything without parking costs except two cases above
    shortterm = "shortterm"                 # accesses with parking costs
    unknown = "unknown"                     # no access at all (unregistered shortterm parker)
    # in bypass and only permitted garages, users entered via external system (bypass system, key, ...)
    # Not used by access services
    external = "external"


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
    vehicle: AccessRequestVehicle                                           # vehicle data
    vehicle_id: Optional[str] = None                                        # vehicle id, if known (for event linking)
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())  # check if access valid at this time

    _tz_timestamp = timezone_validator("timestamp")


class AccessCheckRejectReason(str, Enum):  # see DEV-A-916
    wrong_gate = "wrong_gate"  # no valid at this gate
    wrong_time = "wrong_time"  # no valid at this time
    custom = "custom"  # some access service specific reason for rejection


class AccessCheckAccess(OpenModuleModel):
    id: str                            # id of the access
    group_id: Optional[str]            # id for group-passback, in Digimon Contract ID, optional for 3rd Party Backends
    group_limit: Optional[int] = Field(None, ge=1)  # group_limit must be greater or equal 1
    customer_id: Optional[str]         # in Digimon Customer ID, optional for 3rd Party Backends
    car_id: Optional[str]              # in Digimon Customer Car ID, optional for 3rd Party Backends
    source: str                        # Access Service providing the access
    access_infos: Dict                 # Infos, which are added everywhere for later usage
    parksettings_id: Optional[str]     # None is no cost entries and access at any gate
    clearing: Optional[str]            # Clearing
    clearing_infos: Optional[dict]     # Infos, which are added everywhere for later usage when using clearing
    category: AccessCategory           # category used for sorting and eventlog
    used_medium: Medium                # medium of the access
    access_data: Dict                  # complete access data, will be used only for display and debug purposes

    accepted: bool                     # if access service decided access can enter
    reject_reason: Optional[AccessCheckRejectReason]  # only if not accepted: reason for not accepted
    # additional infos shown in events if reject reason is "custom". Required if reject_reason == "custom"
    supplementary_infos: Optional[str]

    @root_validator(skip_on_failure=True)
    def root_validation(cls, values):
        # if category is handauf, medium_display_name must be set
        if values["category"] == AccessCategory.handauf and "medium_display_name" not in values["access_infos"]:
            raise ValueError("medium_display_name must be set if category is handauf")
        if values["category"] == AccessCategory.external:
            raise ValueError("category external is not allowed for accesses")
        if values["group_limit"] is not None and values["group_id"] is None:
            raise ValueError("group_limit must not be set without group_id")
        if values["category"] in [AccessCategory.shortterm, AccessCategory.unknown] \
                and values["group_limit"] is not None:
            raise ValueError("group_limit must not be set for shortterm and unknown accesses")
        if values.get("reject_reason") == AccessCheckRejectReason.custom and not values.get("supplementary_infos"):
            raise ValueError("supplementary_infos must be set if reject_reason is custom")
        return values


class AccessCheckResponse(OpenModuleModel):
    success: bool
    accesses: List[AccessCheckAccess] = []  # list of all matched accesses (including already rejected ones)
