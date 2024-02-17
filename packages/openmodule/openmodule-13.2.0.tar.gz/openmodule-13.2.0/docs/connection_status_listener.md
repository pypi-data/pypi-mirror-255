# ConnectionStatusListener

[TOC]

For some functionality we need to know if we have an active connection to the server or in the case of bridged installations if we have a connection to the main compute unit.
For this you can use the ConnectionStatusListener, which will be automatically created in the core.

## Connection Status

The connection to the server has 4 different states:
* **online:** Connection active
* **shutdown:** The connection was just lost
* **offline:** The connection is inactive for some time
* **startup:** We just left the offline state with an active connection

The bridge status only consists of 2 different states:
* **online:** Connection to the main compute unit
* **offline:** No connection to the main compute unit


## Behaviour

### General

* In our system the connection status is published periodically (10s)
* If no message is sent for 1min, the listener automatically switches to *shutdown*
* For 5min after we restored the connection from *offline*, the connection status will be *startup*
* Reconnecting while *shutdown* will directly yield the *online* status
* The *offline* can only be set directly with a message, there is no timeout
* Requesting the status before a message was received (e.g. after startup), will trigger an RPC to get the current status
* You need to poll the connection status yourself, there are no callbacks (processed by internal message queue, no callbacks allowed)

### Bridge sub units

* If the connection to the main unit is lost, the connection status will be set to *shutdown* automatically
* Messages and RPC responses are automatically patched with the bridged status



## Usage

### Blocking usage
```python

core: OpenModuleCore
while True:
    core.connection_listener.wait_for_change()
    current_connection_status = core.connection_listener.get()
    # on slaves
    current_bridge_status = core.connection_listener.get_bridge()
    do_something_with_status(current_connection_status, current_bridge_status)
```

### Check if changed since last check

```python
import time

core: OpenModuleCore
while True:
    if core.connection_listener.changed("test_id"):  # if used in a class, .changed(id(self)) is a good idea
        task_on_connection_change()
    do_other_regular_stuff()
    time.sleep(1)
```


