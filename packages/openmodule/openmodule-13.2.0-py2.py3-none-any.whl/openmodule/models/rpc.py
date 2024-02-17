from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID

from openmodule.models.base import ZMQMessage, OpenModuleModel


class RPCRequest(ZMQMessage):
    rpc_id: UUID
    resource: Optional[str]
    request: Optional[Dict]


class RPCResponse(ZMQMessage):
    rpc_id: Optional[UUID]
    response: Any


class RPCServerError(str, Enum):
    handler_error = "handler_error"
    validation_error = "validation_error"
    filter_error = "filter_error"
    error = "error"  # this is from RPCServer (the WebServer, not an RPCServer on the device)


class RPCErrorResult(OpenModuleModel):
    status: RPCServerError
    error: Optional[str]
    exception: Optional[Any]


class ServerRPCRequest(OpenModuleModel):
    rpc: str
    data: Any
