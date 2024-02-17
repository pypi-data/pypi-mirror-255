# Eventlog events

[TOC]

If you want to send an important event to the eventlog, which runs in the cloud, you can use the `send_event` function.

The `send_event` has the following signature:
```python
def send_event(infos: EventInfo, message: str, **message_kwargs: MessageKwarg):
    pass
```

Tne eventlog event does need some meta information, which is provided by the `EventInfo` class.
The `message` is a string, which can contain placeholders for the `MessageKwarg` objects.
The `MessageKwarg` objects are used to replace the placeholders in the message string.

## EventInfo

```python
class EventInfo(OpenModuleModel):
    type: str  # a category for icons and grouping, must contain at least one "_", hierarchy via prefix
    timestamp: datetime
    gate: Optional[str]
    license_plate: Optional[str]  # anonymized with type lpr
    license_plate_country: Optional[str]
    session_id: Optional[str]
    related_session_id: Optional[str]
    vehicle_id: Optional[str]
    price: Optional[int]  # cents
```

**⚠ Attention:** The `type` field must contain at least one `_` to be able to group events in the eventlog.
You should use a common prefix for all events of the same type, e.g. `lpr` for license plate recognition events.

If you are sending an event to the eventlog provide as much information as possible, but only the `type` field is required.

The fields:
  * gate
  * session_id
  * vehicle_id

Are used by the eventlog to group events together for a common a vehicle.

To send an event in correct format to the eventlog, just use the `send_event` function. Create the event infos, use the 
`EventInfo.create` function

## Message and MessageKwarg

The message is a string, which can contain placeholders for the `MessageKwarg` objects.
All messages have to be translated. A guide how to translate messages can be found
in the [translation guide](translation.md).

The `MessageKwarg` arguments have to be enclosed by `{{ arg }}` in the message string.
The double curly braces are used to distinguish the placeholders from other curly braces in the message string.
This is how Python escapes the curly brackets in strings.

The `MessageKwarg.lpr` is special because this argument will be anonymized.

## Example

```python
from openmodule.utils.eventlog import send_event, EventInfo, MessageKwarg
from openmodule.utils.translation import _

welcome_infos = EventInfo.create("example_welcome", license_plate=license_plate, session_id=session_id)
send_event(welcome_infos, _("Welcome to \"{name}\": {{lpr}}").format(name="Jurassic Park"),
           lpr=MessageKwarg.lpr(license_plate))


welcome_infos = EventInfo.create("example_bye", license_plate=license_plate, session_id=session_id)
send_event(welcome_infos, _("We hope you had a nice time. Goodbye {{lpr}}."),
           lpr=MessageKwarg.lpr(license_plate))
```
