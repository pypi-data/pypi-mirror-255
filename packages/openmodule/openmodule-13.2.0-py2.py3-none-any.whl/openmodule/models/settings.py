from typing import List, Any, Optional, Dict

from openmodule.models.base import OpenModuleModel, ZMQMessage


class SettingsGetResponseValue(OpenModuleModel):
    value: Any
    success: bool
    error: Optional[str]


class SettingsGetRequest(OpenModuleModel):
    key: str
    scope: str = ""


SettingsGetResponse = SettingsGetResponseValue


class SettingsGetManyRequest(OpenModuleModel):
    key: List[str]
    scope: str = ""


class SettingsGetManyResponse(OpenModuleModel):
    settings: Dict[str, SettingsGetResponseValue]


class SettingsChangedMessage(ZMQMessage):
    type = "changed"
    changed_keys: List[str]  # is <key>/<scope>
