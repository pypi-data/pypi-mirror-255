### Anonymization

[TOC]

The openmodule framework uses rpc requests and messages to trigger the anonymization of data.

* **Message:** ONLY the DSGVO device service can send a AnonymizeMessage (topic: `privacy`).  
  The message includes a session_id and vehicle_ids to delete.
* **RPC Request:** You can send an AnonymizeRequest with channel=`privacy`, type=`anonymize` to the DSGVO container.
  This request only includes session_ids.
  The DSGVO container will then match vehicle_ids to the session_ids and redistribute the request with the prior
  mentioned message.

A container with sensitive data then needs to implement the message listener for the privacy messages (see example).

##### Example 1

The controller checked that a parking session was finished and fully paid. After a specified time, the DSGVO relevant
data has to be anonymized. The controller then triggers the anonymization.

```python
request = AnonymizeRequest(session_ids=[session_id])
result = core.rpc_client.rpc("privacy", "anonymize", request)
if result.response.status == "ok":
    self.log.info(f"Anonymized session {session_id}")
```

##### Example 2

The controller checked that a parking session was finished and fully paid. After a specified time, the DSGVO relevant
data has to be anonymized. The controller then triggers the anonymization.

```python
msg = AnonymizeMessage(vehicle_ids=[vid1, vid2])
self.core.publish(msg, "privacy")
```

The DSGVO container receives the request, matches session_ids with vehicle_ids and publishes the anonymization message.
It also listens on said messages and deletes vehicle images based on the vehicle_ids in the message.

```python
core.messages.register("privacy", AnonymizeMessage, anonymize_data)


def anonymize_data(message: AnonymizeMessage):
    for vid in message.vehicle_ids:
        delete_vehicle_image_by_vehicle_id(vid)
```

**IMPORTANT** You still have to take care of data retention in each service separately, meaning you have to delete data
independently of these anonymization messages.
i.e. the DSGVO service deletes data if we need disk space or the eventlog deletes events after 30 days by default