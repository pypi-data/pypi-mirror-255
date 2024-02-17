# Utils

[TOC]

Here you can find some documentation of the other features of the Openmodule library.

## Presence

Helper class for listening to presence messages.

```python
from openmodule.utils.presence import PresenceListener

presence_listener = PresenceListener(core.messages)
presence_listener.on_enter.append(some_function)
```

### Databox Upload

In the openmodule we have a utils function to simplify the upload with the databox service. The prerequisite is, 
that the upload folder `/data/om_service_databox_1/upload` is mounted correctly in the compose file to the `settings.DATABOX_UPLOAD_DIR` (default: `/upload`)

```python
from openmodule.utils.databox import upload

upload("/tmp/asdf.txt", "/enforcement/test/asdf.txt")
upload("/tmp/bsdf.csv", "exports/")  # same as exports/bsdf.csv as filename is taken from source if dst ends with /
```

docker-compose.yml example snippet
```yaml
    volumes:
    - /data/om_service_databox_1/upload/:/upload/
```

## Scheduling of Jobs

See [here](https://github.com/ts-accessio/schedule/tree/dateutil-support)

**⚠ Attention:** Do not import `schedule` yourself, openmodule imports 
the schedule version with dateutil support for you. 

## Documentation

Openmodule >= 3.0.5 features automatic generation of RPC and Message Schemas including their models. The generation uses
data that is generated during the test runs to create an OpenApi Schema. Your RPCs and Message handlers are
automatically documented if:

* You use the message dispatcher of the core (`OpenModuleCoreTestMixin`)
* You use the RPCServer of Openmodule

You can also register models yourself if you want them documented, but you may need to save the Schema in this case:

```python
from openmodule.utils.schema import Schema

Schema.save_model(Model)
Schema.save_rpc(channel, type, request, reqponse, handler)
Schema.save_message(topic, message_class, handler, filter)

Schema.to_file()
```

With default parameters, you need to document your handler functions with a doc string, that is then included as a
description.

