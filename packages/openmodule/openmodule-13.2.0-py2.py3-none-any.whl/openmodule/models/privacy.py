from datetime import datetime, timedelta
from typing import List
from typing import Optional

from openmodule.models.base import OpenModuleModel
from openmodule.models.base import ZMQMessage


class AnonymizeMessage(ZMQMessage):
    type: str = "anonymize"
    session_id: Optional[str]
    vehicle_ids: Optional[List[str]] = []


class AnonymizeRequest(OpenModuleModel):
    session_ids: List[str]


class AnonymizeResponse(OpenModuleModel):
    pass


class PrivacyTime(OpenModuleModel):
    minutes: Optional[int]
    hours: Optional[int]
    days: Optional[int]

    def time(self) -> Optional[datetime]:
        kwargs = {k: v for k, v in self.dict().items() if v}
        return (datetime.utcnow() - timedelta(**kwargs)) if kwargs else None

    def timedelta(self) -> Optional[timedelta]:
        kwargs = {k: v for k, v in self.dict().items() if v}
        return timedelta(**kwargs) if kwargs else None


class PrivacySettings(OpenModuleModel):
    paid: PrivacyTime = PrivacyTime(days=1)
    unpaid: PrivacyTime = PrivacyTime(days=90)
    registered_free: PrivacyTime = PrivacyTime(days=30)
    pay_via_invoice: PrivacyTime = PrivacyTime(days=30)
    open: PrivacyTime = PrivacyTime(days=90)
    free: PrivacyTime = PrivacyTime(minutes=5)
    honest_payment: PrivacyTime = PrivacyTime(days=90)
    erroneous: PrivacyTime = PrivacyTime(days=30)
    rejected: PrivacyTime = PrivacyTime(days=7)

    def max_timedelta(self):
        return max([x.timedelta() for x in self.__dict__.values() if isinstance(x, PrivacyTime)])
