from datetime import datetime

from openmodule.config import settings
from openmodule.models.access_service import AccessCheckRequest, SessionStartMessage, SessionFinishMessage, \
    AccessCheckResponse, AccessRequestVehicle
from openmodule.utils.access_service import AccessServiceWithSessions
from openmodule.utils.matching import MatchingConfig
from openmodule_test.core import OpenModuleCoreTestMixin
from openmodule_test.database import SQLiteTestMixin
from openmodule_test.eventlistener import MockEvent
from openmodule_test.settings import SettingsMocker


class TestAccessServiceWithSessions(AccessServiceWithSessions):
    __test__ = False

    auth_request_request_model = AccessCheckRequest

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_processed = MockEvent()

    checked_in = []
    checked_out = []
    accessed = []
    access_by_lpr = {}
    access_by_qr = {}
    access_by_nfc = {}
    access_by_pin = {}

    def wait_for_message_process(self):
        """
        waits for at least one message to be processed
        """
        self.message_processed.wait_for_call()

    def check_in_session(self, message: SessionStartMessage):
        if message.entry_data.get("gate") == "error":
            self.message_processed()
            raise Exception("test_exception")
        self.checked_in.append(message)
        self.message_processed()

    def check_out_session(self, message: SessionFinishMessage):
        if message.exit_data.get("gate") == "error":
            self.message_processed()
            raise Exception("test_exception")
        self.checked_out.append(message)
        self.message_processed()

    def rpc_check_access(self, request: AccessCheckRequest, _) -> AccessCheckResponse:
        """
        Test Access Service auth request handler
        """
        self.accessed += [request]
        if request.gate:

            if request.gate == "exception":
                raise Exception("test_exception")
            elif request.gate == "empty":
                return AccessCheckResponse(success=True, accesses=[])
            elif request.gate == "offline":
                return AccessCheckResponse(success=False, error="offline", accesses=[])
            elif request.gate == "error":
                return AccessCheckResponse(success=False, error="error", accesses=[])

        accesses = []
        if request.vehicle.lpr and request.vehicle.lpr.id in self.access_by_lpr:
            accesses.append(self.access_by_lpr[request.vehicle.lpr.id])
        if request.vehicle.qr and request.vehicle.qr.id in self.access_by_qr:
            accesses.append(self.access_by_qr[request.vehicle.qr.id])
        if request.vehicle.nfc and request.vehicle.nfc.id in self.access_by_nfc:
            accesses.append(self.access_by_nfc[request.vehicle.nfc.id])
        if request.vehicle.pin and request.vehicle.pin.id in self.access_by_pin:
            accesses.append(self.access_by_pin[request.vehicle.pin.id])
        return AccessCheckResponse(success=True, accesses=accesses)


class AccessServiceWithSessionsTestMixin(OpenModuleCoreTestMixin):
    """
    AccessServiceTestMixin with helper functions for testing access services
    * set the access_service_class
    """
    access_service_class = None

    @classmethod
    def setUpClass(cls) -> None:
        assert cls.access_service_class, "set a access_service_class"
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.access_service = self.access_service_class()
        self.transaction_count = 0
        self.messages_by_transaction = {}
        self.zone_count = {}

    def tearDown(self):
        super().tearDown()

    def check_auth(self, vehicle: AccessRequestVehicle, **kwargs):
        """
         standard check_auth call
        : param kwargs: Parameters to overwrite in the AccessRequest
        """
        kwargs.setdefault("name", settings.NAME)
        kwargs["vehicle"] = vehicle
        request = AccessCheckRequest(**kwargs)
        return self.access_service.rpc_check_access(request, None)

    def send_session_start_message(self, gate="gate1", medium_id="GARIVO1", medium_type="lpr", zone_id="zone_1",
                                   user_id="user-1", timestamp=None, session_id="session-1", group_id=None,
                                   customer_id=None, car_id=None):
        entry_data = dict(used_medium=dict(id=medium_id, type=medium_type), gate=gate)

        message = SessionStartMessage(zone_id=zone_id, user_id=user_id, id=session_id, cost_table={}, serviceable=True,
                                      entry_time=timestamp or datetime.utcnow(), entry_data=entry_data,
                                      group_id=group_id, customer_id=customer_id,
                                      car_id=car_id)
        self.core.publish(message, "session")

    def send_session_finish_message(self, gate="gate2", medium_id="GARIVO1", medium_type="lpr", zone_id="zone_1",
                                    user_id="user-1", timestamp=None, session_id="session-1", group_id=None,
                                    customer_id=None, car_id=None):
        exit_data = dict(used_medium=dict(id=medium_id, type=medium_type), gate=gate)
        message = SessionFinishMessage(zone_id=zone_id, user_id=user_id, id=session_id, cost_table={}, serviceable=True,
                                       exit_time=timestamp or datetime.utcnow(), exit_data=exit_data, entry_data={},
                                       entry_time=datetime.utcnow(), group_id=group_id,
                                       customer_id=customer_id, car_id=car_id)

        self.core.publish(message, "session")


class AccessServiceWithDatabaseTestMixin(OpenModuleCoreTestMixin, SQLiteTestMixin):
    """
    AccessServiceTestMixin with helper functions for testing access services
    * set the access_service_class
    """
    access_service_class = None
    matching_config = MatchingConfig()
    settings = SettingsMocker({})

    @classmethod
    def setUpClass(cls) -> None:
        assert cls.access_service_class, "set a access_service_class"
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.access_service = self.access_service_class(self.database, self.matching_config, self.settings, 300)

    def tearDown(self):
        self.access_service.shutdown()
        super().tearDown()
