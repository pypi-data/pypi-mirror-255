# Openmodule Testing

[TOC]

We provide multiple Mixins and Util classes for test purposes in openmodule-test.

**⚠ Attention:** You need to set the environment variable `TESTING=True` for all tests!

## Settings

The ZMQTestMixin already sets the settings up for you with the module defined in `src/config`.

As per default the message queue run `inproc` for speeding up test cases.
You can change the protocol to TCP by overwriting the `protocol` class member variable.

To customize the settings during testing you have 3 options:

```python
# class decorator
@override_settings(A="B")
class Test(ZMQTestMixin):

    # function decorator
    @override_settings(B="C")
    def test(self):
        self.assertEqual("B", settings.A)
        self.assertEqual("C", settings.B)

        # context
        with override_context(B="A"):
            self.assertEqual("A", settings.B)
        self.assertEqual("C", settings.B)
```

Keep in mind: Default parameters of functions are set at import, so override_settings does not work for them.

The ZMQTestMixin also provides automatic settings override with the `zmq_config(**kwargs)` method

## Mixin

### OpenModuleCoreTestMixin

This mixin creates a OpenModule instance in the `core` member variable.
It also waits until your device service is ready using the `wait_for_health` method.

```python
def setUp():
    super.setUp()
    ...
    self.core = init_openmodule(...)
    self.zmq_client.subscribe("healthpong")
    self.wait_for_health(self.core.config.NAME)
```

This mixin inherits from `ZMQTestMixin` and therefore provides the class member variable `topics`.
The mixin automatically subscribes to the given list of topics, and you can use the `wait_for_message_on_topic` or
`wait_for_message` method in the test case.

In the example below our app `MyWelcomeMessageHandle` listens to the `WelcomeMessage` with type "hi"
and responds with a `ByeMessage` with type "bye". It should simulate that you are using an external message and
react to it.

```python
class WelcomeMessage(ZMQMessage):
    type: str = "hi"
    message: str


class ByeMessage(ZMQMessage):
    type: str = "bye"
    message: str


class MyWelcomeMessageHandler:
    def __init__(self, core: OpenModuleCore):
        self.core = core
        self.core.messages.register_handler("welcome", WelcomeMessage, handler=self.welcome_handler,
                                            filter=self.filter_for_hi)

    @staticmethod
    def filter_for_hi(message: dict) -> bool:
        return message.get("type") == "hi"

    def welcome_handler(self, _: WelcomeMessage):
        self.core.publish(ByeMessage(message="Bye!"), "welcome")


class ExampleTopicTestCase(OpenModuleCoreTestMixin):
    topics = ["welcome"]

    def setUp(self):
        super().setUp()
        self.app = MyWelcomeMessageHandler(self.core)

    @staticmethod
    def filter_for_bye(topic: str, message: dict) -> bool:
        return topic == "welcome" and message.get("type") == "bye"

    def test_topic(self):
        self.core.publish(WelcomeMessage(message="Hello World!"), "welcome")
        self.zmq_client.wait_for_message(self.filter_for_bye)
```

### RPCServerTestMixin

Mixin providing rpc and messaging functionality

```python
class Test(OpenModuleCoreTestMixin, RPCServerTestMixin):
    rpc_channels = ["backend"]

    def setUp(self):
        super().setUp()
        self.server = RPCServer(context=self.zmq_context())
        self.server.run_as_thread()
        # register rpcs here
        self.server.register_handler("test", "dummy", OpenModuleModel, OpenModuleModel, self.dummy_callback)
        self.wait_for_rpc_server(self.server)

    def dummy_callback(self, request: OpenModuleModel, _) -> OpenModuleModel:
        """
        dummy callback. docs string MUST NOT be forgotten
        """
        return OpenModuleModel()

    def tearDown(self):
        self.server.shutdown()
        super().tearDown()
```

### SQLiteTestMixin

Mixin that takes a database or creates one and cleans it up after each test.

```python
# base database that gets reset
class Test(SQLiteTestMixin):
    pass


# use other database
class Test(SQLiteTestMixin, OpenModuleCoreTestMixin):
    create_database = False
    init_kwargs = dict(database=True)

    def setUp(self):
        super().setUp()
        self.database = self.core.database
```

### AlembicMigrationTestMixin

Mixin for testing alembic migrations. Tests start with a clean database without any data and can migrate up and down.

You can also provide your own sqlite3 database that will be copied for each test.

**⚠ Do not use the database models defined in your app for these tests.** 
Instead use the `AlembicMigrationTestMixin.get_model`method to get the model from the database schema. 
Your Source code will not work with models from a different database revision. Do not call any functions that rely on
the database models in your tests.

```python
class Test(AlembicMigrationTestMixin):
    def test_migrations(self):
        self.migrate_up()  # migrate to latest / head
        my_db_model = self.get_model("my_model")  # get model from database schema using table name
        with self.database as session:
            session.add(my_db_model())
            session.commit()
        self.migrate_down()  # migrate to base
        self.migrate_up("1dff3f3f3f3f")  # migrate to specific revision


class TestWithDB(AlembicMigrationTestMixin):
    existing_database = "../tests/test.db"

    def test_migrations(self):
        self.assertEqual(self.current_revision(), "1dff3f3f3f3f")
        my_db_model = self.get_model("my_model")  # get model from database schema using table name
        with self.database as session:
            session.add(my_db_model())
            session.commit()
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            self.migrate_down()  # migrate to base -> fails because of some constraint that was removed in 1dff3f3f3f3f
```

### AlertTestMixin

Mixin to for dealing with alerts

```python
class AlertTestCase(AlertTestMixin):
    topics = ["alert"]
```

### BackendTestMixin (Deprecated)

Mixin with core creation, backend creation and backend util functions

```python
class Test(BackendTestMixin):
    backend_class = Backend
```

### HealthTestMixin

Mixin for receiving and checking health status, included in CoreMixin

```python
class Test(HealthTestMixin):
    topics = ["healthpong"]
```

## Utils

### ApiMocker

Base mocker class for simulating http requests

```python
class Mocker(ApiMocker):
    host = config.SERVER_URL

    def mock(self):
        def cb(request, context):
            return {}

        self.mocker.get(self.server_url("abc"), json=cb)


class Test(TestCase):
    @requests_mock.Mocker(real_http=False)
    def test_check_in_out(self, m):
        res = requests.get(config.host + "abc")
```

### MockEvent

Check if function was called, i.e. in a listener -> do not forget resetting

```python
event = MockEvent()
some_event_listener.append(event)
do_trigger_event()
event.wait_for_call()
event.reset_call_count()
```

### VehicleBuilder

Util class for generating vehicles

```python
vehicle = VehicleBuilder().lpr("A", "G ARIVO1")
```

### PresenceSimulator

Util class for simulating presence messages

```python
presence_sim = PresenceSimulator("gate_in", Direction.IN, lambda x: self.zmq_client.send("presence", x))
presence_listener = PresenceListener(core.messages)
on_enter = MockEvent()
presence_listener.on_enter.append(on_enter)
presence_sim.enter(self.presence_sim.vehicle().lpr("A", "G ARIVO1"))
on_enter.wait_for_call()
```

### MockRPCClient

This is a fake RPCClient where you can either specify callback functions for RPCs or even the responses.
It returns the result of the matching callback, if available, otherwise the value in the matching response else
raises TimeoutError.

```python
def callback(res: SomeRequest, _):
    return SomeResponse()


rpc_client = MockRPCClient(callbacks={("channel", "type"): callback},
                           responses={("channel2", "type2"): SomeResponse2})
res = rpc_client.rpc("channel", "type", SomeRequest(), SomeResponse)  # returns result of callback
future = rpc_client.rpc_non_blocking("channel2", "type2", SomeRequest())  # returns result of callback
res = future.result(SomeResponse2)  # returns value of rpc_client.responses[("channel2", "type2")]

rpc_client.responses = {("channel2", "type2"): SomeResponse2}}  # you can edit responses and callbacks after creation
```

For integration test you can replace the RPCClient of the core

```python
core().rpc_client = MockRPCClient()
```

## Main Test

Minimal Example

```python
from signal import SIGINT


class MainTest(MainTestMixin):
    def test_keyboard(self):
        try:
            with self.assertLogs() as cm:
                process = self.start_process(main_wrapper)
                self.wait_for_health()

                self.send_signal_to_process(process, SIGINT)
                self.assertCleanShutdown(process, shutdown_timeout=3)
        except Exception as e:
            for line in cm.output:
                print(line)
            raise e

        self.assertIn("KeyboardInterrupt", str(cm.output))
```

This is a boiler plate for a main test, which starts the service in it's entirety. We want to be sure that
a service quickly and cleanly shuts down when receiving a SIGINT. This test will fail if the service does not
shut down within 3 seconds and print that it hase received a KeyboardInterrupt.

### Examples

Since main tests are somewhat complex, we provide some examples for different use cases.

**Wait for an RPC server to be started, and send a test RPC. Also ensure that the service sends a specific message on start and stop (basic backend test case).**

```python 
class MainTest(RPCServerTestMixin, MainTestMixin):
    def test_sigterm(self):
        with self.assertLogs() as cm:
            process = self.start_process(main_wrapper)

            try:
                # on startup the backend must register
                register_request = self.zmq_client.wait_for_message_on_topic("backend")
                self.assertEqual("register", register_request.get("type"))

                # wait for the rpc server to become responsive
                self.wait_for_rpc_response("backend", "auth", AccessRequest(name=settings.NAME, medium_id="GARIVO1", medium_type="lpr"), AccessResponse)

                # make a test request
                response = self.rpc("backend", "auth", AccessRequest(name=settings.NAME, medium_id="GARIVO1", medium_type="lpr"), AccessResponse)
                self.assertEqual("GARIVO1", response.medium_id)
                
            finally:
                self.send_signal_to_process(process, signal.SIGTERM)
                self.assertCleanShutdown(process)

        self.assertIn("shutting down", str(cm.output))

        # on shutdown the backend must have unregistered
        register_request = self.zmq_client.wait_for_message_on_topic("backend")
        self.assertEqual("unregister", register_request.get("type"))

```

**Wait for an HTTP server to be started**

```python 
class MainTest(MainTestMixin):
    def wait_for_http(self):
        for x in range(10):
            try:
                requests.get("http://localhost:1881/internal/complete/pins", timeout=1)
                break
            except:
                pass
            time.sleep(1)
        raise Exception("HTTP server did not start")

    def test_keyboard(self):
        self.signal_in_function(main_wrapper, KeyboardInterrupt, raise_exception_after=0.5, shutdown_timeout=3)
        try:
            with self.assertLogs() as cm:
                process = self.start_process(main_wrapper)

                self.wait_for_health()
                self.wait_for_http()

                self.send_signal_to_process(process, SIGINT)
                self.assertCleanShutdown(process, shutdown_timeout=3)
        except Exception as e:
            for line in cm.output:
                print(line)
            raise e

        self.assertIn("KeyboardInterrupt", str(cm.output))
```

### Pitfalls

#### Uvicorn Log Output Not Captured

If you have an Uvicorn application and you want to assert on the Uvicorn log output, e.g. "Finished server process",
then the Main Test can fail.

A fix for this issue is to provide a `log_config` argument for the method `uvicorn.run()`.

```python
 log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}
try:
    uvicorn.run(app, host="0.0.0.0", port=5556, log_config=log_config)
except KeyboardInterrupt:
    logging.warning("KeyboardInterrupt received, shutting down...")
finally:
    # shutdown routines
    pass
```

Another fix is setting the `log_config` to `None`, but with this setting the Uvicorn log output is disabled
for `python -m tox` command.

## Exit with Error 112

Whenever the RPCServer finds a RPCResponse model containing a `status` field, a log line is printed and the process is
terminated with error code 112. The log line might not be printed in some cases, so watch out for 112

