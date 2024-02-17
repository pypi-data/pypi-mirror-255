# RPC Server

[TOC]

## Filters and Daemons

The RPC server if you do not register any filters answers to all requests for a given channel / type. This is fine
if the application provides one service, such as for example the parking logic. However, if you have multiple
services, or daemons (see below) each service _must_ register a filter so it only answers to requests which are
intended for it. Otherwise multiple services would answer the same RPC which is not what you want.

#### Per-Gate Case

Usually this happens if a service is started once per gate. So it is responsible for this gate only.
In this case the RPC request _must_ include some information about which gate it is targeting. The filter
in the service should then only respond to requests which are targeting it's gate.

```python
class GateControlRequest(OpenModuleModel):
    gate: str
    
class GateControlResponse(OpenModuleModel):
    success: bool
    error: Optional[str]

def open_gate(request: GateControlRequest) -> GateControlResponse:
    """Try to open the gate"""
    if try_to_open_gate(request.gate):
        return GateControlResponse(success=True)
    else:
        return GateControlResponse(success=False, error="Could not open gate")
    

server = RPCServer(...)
server.add_filter(lambda request: request.gate == "gate")
server.register_rpc('gate_control', 'open_gate', GateControlRequest, GateControlResponse, open_gate)
```

The `register_rpc` method also has the parameter `register_schema`.
This parameter automatically create a schema for your rpc and its models.
For more information see [documentation](utils.md#documentation).

**⚠ Attention:** You have to add a [Docstring](https://peps.python.org/pep-0257/#what-is-a-docstring)
to your handle function.

#### Daemon Case

A daemon is started once per compute unit. Often times the damon is then responsible for rpc requests which target
either hardware devices connected to this compute unit, or other data which is only available at this compute unit.
Examples for this are:

* The relay service which relays the video stream but only for cameras which are connected to it's compute unit
  ```python
  class GetVideoStreamRequest(OpenModuleModel):
      camera_hardware_package: str
   
  hardware_package = [x.name for x in package_reader.list_by_hardware_type('camera', compute_id=settings.COMPUTE_ID)]
  server = RPCServer(...)
  server.add_filter(lambda request: request.camera_hardware_package in hardware_package)
  server.register_rpc('video_stream', 'get_video_stream', GetVideoStreamRequest, GetVideoStreamResponse, self.get_video_stream)
  ```

## Executor

The RPC server supports running it's requests multithreaded. This can be necessary if for example your rpc
calls a different service, which tries to call your service again. This commonly happens in larger services.

By default the rpc requests are run in the thread of the RPC server itself. You can however pass a
executor for multithreaded execution.

```python
from concurrent.futures import ThreadPoolExecutor
from openmodule.rpc import RPCServer


executor = ThreadPoolExecutor(max_workers=1)
my_server = RPCServer(core().context, executor=executor)
```

# RPC Client

## Blocking RPC Requests

The rpc client can be used to call functions which other services provide via an [RPC Server](#RPC Server). The RPC
client is accessible through the `OpenModuleCore` instance. If the RPC fails (timeout, validation errors,
exception in handler on server), an exception is raised. If successful the result is parsed to the response type.

```python
try:
    result = core().rpc_client.rpc("channel", "test", SomeRequest(), SomeResponse)  # result is of type SomeResponse
except RPCClient.Exception as e:
    logging.exception("Failed to do RPC channel:test")
```

A blocking RPC call is equivalent to calling `.result()` on a non-blocking call:

```python
try:
    result = rpc_client.rpc("channel", "test", SomeRequest(), SomeResponse)
except RPCClient.Exception as e:
    logging.exception("Failed to do RPC channel:test")
# -> equivalent
try:
    result = rpc_client.rpc_non_blocking("channel", "test", SomeRequest()).result(SomeResponse)
except RPCClient.Exception as e:
    logging.exception("Failed to do RPC channel:test")
```

## Non Blocking RPC Requests

By using `rpc_non_blocking(...)` the rpc call returns a `RPCEntry` object, which can be used for waiting for an RPC
response asynchronously.

```python
future = client.rpc_non_blocking("channel", "test", SomeRPCRequest())

# The future object can be used to wait for the RPC result asynchronously
try:
    future.result(timeout=1)
except RPCClient.Exception as e:
    logging.exception("Failed to do RPC channel:test")

# You can also check if a response is available 
future.done()  # True
```

### About Timeouts

Please note that you **cannot extend the timeout, after sending the rpc request**. For example if you send an PRC
request with a timeout of 5 seconds:

```python
future = client.rpc_non_blocking("channel", "test", SomeRPCRequest(), timeout=5)
```

You cannot wait for longer than 5 seconds.

```python
future.result(timeout=10)

# UserWarning: You cannot extend the timeout of an RPC after sending the request. The timeout will be limited to at most the initial timeout.
#  result.result(timeout=2)
```

This is because the RPC Client's worker discards timed out rpc requests in order to conserve memory. If however a
response was already received within the timeout, calling `result()` will not trigger a timeout error.

## Cancelling RPC Requests

This is only possible for non-blocking RPC requests. However every blocking RPC request can be written as non-blocking.
Use `RPCClient.RPCEntry.cancel()`. The `RPCClient.RPCEntry.result()` function will raise a `RPCClient.CancelError`
exception

```python
future = None


def do_rpc():
    global future
    future = rpc_client.rpc_non_blocking("channel", "test", SomeRPCRequest(), timeout=1000)
    try:
        future.result()
    except RPCClient.CancelError:
        print("Cancelled")
    except RPCClient.Exception:
        logging.exception("Failed to do RPC channel:test")


def cancel_rpc():
    future.cancel()
```
