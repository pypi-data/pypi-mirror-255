# Deprecated

[TOC]

This file holds documentation of deprecated features. It is kept for reference and maybe will be removed in the future.

## Deprecated Utils

### Api (**DEPRECATED**)

We implemented a very basic Api class you can use for http request and that handles errors and authentication. Either
inherit it or create a class.

```python
api = Api(**kwargs)
try:
    res = api.post("some_url", payload=stuff)
except ApiException as e:
    if e.retry:  # <- makes sense to try again - timeouts or server not available ...
        ...
```

### Backend (**DEPRECATED**)

There is also a basic implementation of a backend that provides registration and message passing.

```python
class MyAccessService(AccessService):
    def __init__(self):
        super().__init__(implements_session_handling=...)
        ...

    def rpc_check_access(self, request: AccessRequest) -> AccessCheckResponse:
        ...

    # session handling
    def check_in_session(self, message: SessionStartMessage):
        ...

    def check_out_session(self, message: SessionFinishMessage):
        ...

    def session_error_message(self, message: Union[SessionDeleteMessage, SessionIncompleteMessage,
                                                   SessionExitWithoutEntryMessage]):
        ...
```

### Alerting (**DEPRECATED**)

The new core also includes an alert handler.

```python
core.alerts.send(...)
alert_id = core.alerts.get_or_add_alert_id(...)
core.alerts.send_with_alert_id(alert_id, ...)
```
