import os
import uuid
from datetime import datetime, timedelta
from unittest import TestCase

import freezegun
from dateutil.parser import parse
from settings_models.settings.common import Gate, GateType, ParkingArea, ShorttermLimitType, Parksetting
from sqlalchemy.ext.declarative import declarative_base

from openmodule.config import settings
from openmodule.models.access_service import AccessCheckRequest, AccessTime, AccessCheckAccess, AccessCategory, \
    AccessRequestVehicle, AccessCheckResponse
from openmodule.models.vehicle import LPRMedium, LPRCountry, Medium, MediumType
from openmodule.rpc.server import RPCServer
from openmodule.utils.access_service import AccessServiceWithDatabase, AccessModelBase
from openmodule.utils.matching import MatchingConfig
from openmodule_test.access_service import AccessServiceWithSessionsTestMixin, TestAccessServiceWithSessions, \
    AccessServiceWithDatabaseTestMixin
from openmodule_test.eventlistener import MockEvent
from openmodule_test.rpc import RPCServerTestMixin


class WithSessionsFunctionTest(AccessServiceWithSessionsTestMixin, TestCase):
    access_service_class = TestAccessServiceWithSessions

    def test_access(self):
        self.access_service_class.access_by_lpr = {"GARIVO2": dict(id="access-lpr", category=AccessCategory.permanent,
                                                                   accepted=True, access_data={},
                                                                   used_medium=Medium(type=MediumType.lpr, id="GARIVO2"),
                                                                   access_infos={}, source="test")}
        self.access_service_class.access_by_qr = {"qr1": dict(id="access-qr", category=AccessCategory.permanent,
                                                              accepted=True, access_data={},
                                                              used_medium=Medium(type=MediumType.qr, id="qr1"),
                                                              access_infos={}, source="test")}
        self.access_service_class.access_by_nfc = {"nfc1": dict(id="access-nfc", category=AccessCategory.permanent,
                                                                accepted=True, access_data={},
                                                                used_medium=Medium(type=MediumType.nfc, id="nfc1"),
                                                                access_infos={}, source="test")}
        self.access_service_class.access_by_pin = {"pin1": dict(id="access-pin", category=AccessCategory.permanent,
                                                                accepted=True, access_data={},
                                                                used_medium=Medium(type=MediumType.pin, id="pin1"),
                                                                access_infos={}, source="test")}

        vehicle = dict(lpr=dict(id="GARIVO1"))
        result = self.check_auth(vehicle)
        self.assertTrue(result.success)
        self.assertEqual([], result.accesses)

        result = self.check_auth(vehicle, gate="empty")
        self.assertTrue(result.success)
        self.assertEqual([], result.accesses)

        result = self.check_auth(vehicle, gate="error")
        self.assertEqual("error", result.error)
        self.assertEqual([], result.accesses)

        try:
            self.check_auth(vehicle, gate="exception")
        except Exception as e:
            self.assertEqual("test_exception", str(e))

        vehicle = dict(lpr=dict(id="GARIVO2"))
        result = self.check_auth(vehicle)
        self.assertTrue(result.success)
        self.assertNotEqual([], result.accesses)

        vehicle = dict(pin=dict(id="pin1", type="pin"), qr=dict(id="qr1", type="qr"), nfc=dict(id="nfc1", type="nfc"))
        result = self.check_auth(vehicle)
        self.assertTrue(result.success)
        self.assertEqual(3, len(result.accesses))
        for x in result.accesses:
            self.assertIn(x.id, ["access-qr", "access-nfc", "access-pin"])


Base = declarative_base()


class TestAccessModelBase(Base, AccessModelBase):
    __test__ = False
    __tablename__ = "test_access_model"

    @classmethod
    def parse_value(cls, value) -> dict:
        """Parses the value from the server into a dict of {column-name: value}"""
        return value


class TestAccessServiceWithDatabase(AccessServiceWithDatabase):
    __test__ = False
    database_table = TestAccessModelBase

    def db_model_to_access(self, db_model: TestAccessModelBase, used_medium: Medium, request: AccessCheckRequest) \
            -> AccessCheckAccess:
        common_data = dict(id=db_model.id, group_id=db_model.group_id, customer_id=db_model.customer_id,
                           car_id=db_model.car_id, access_infos=db_model.access_infos or {}, source="test",
                           parksettings_id=request.gate, category=AccessCategory.whitelist)
        access_data = dict(matching_scheme=db_model.matching_scheme, matching_version=db_model.matching_version,
                           **common_data)
        return AccessCheckAccess(access_data=access_data, used_medium=used_medium, accepted=True, **common_data)


class WithDatabaseFunctionTest(AccessServiceWithDatabaseTestMixin):
    alembic_path = "../tests/test_access_service_database"
    database_name = "access_service"
    access_service_class = TestAccessServiceWithDatabase
    matching_config = MatchingConfig(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                            "resources/standard_schemes"))

    def setUp(self) -> None:
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_find_lpr_accesses(self):
        with self.database as db:
            db.add(TestAccessModelBase(id="1", lpr_id="G ARIVO 1", lpr_country="A", matching_version=40))
            db.add(TestAccessModelBase(id="2", lpr_id="G ARIVO1", lpr_country="B", matching_version=30,
                                       access_infos={}))
            db.add(TestAccessModelBase(id="3", lpr_id="G:ARIVO1", lpr_country="CH", matching_version=20,
                                       access_infos={}))
            db.add(TestAccessModelBase(id="4", lpr_id="GARIVO1", lpr_country="D", matching_version=20,
                                       access_infos={}))
            db.add(TestAccessModelBase(id="5", lpr_id="GARIVO1", lpr_country="E",
                                       access_infos={}))  # is default 10
            db.add(TestAccessModelBase(id="6", lpr_id="GARIV01", lpr_country="F", matching_version=0,
                                       access_infos={}))
            db.add(TestAccessModelBase(id="7", lpr_id="WARIV01", lpr_country="GR", matching_version=0,
                                       access_infos={}))
            db.add(TestAccessModelBase(id="8", qr_id="QR1", access_infos={}))

        accesses = self.access_service.find_lpr_accesses(LPRMedium(id="G ARIVO 1", country=LPRCountry(code="A")),
                                                         AccessCheckRequest(name=settings.NAME, gate="gate1",
                                                                            vehicle=AccessRequestVehicle()))
        self.assertEqual(5, len(accesses))
        self.assertEqual({"1", "2", "3", "5", "6"}, set([a.id for a in accesses]),
                         AccessCheckRequest(name=settings.NAME, gate="gate1", vehicle=AccessRequestVehicle()))

        accesses = self.access_service.find_lpr_accesses(LPRMedium(id="GARIVO1"),
                                                         AccessCheckRequest(name=settings.NAME, gate="gate1",
                                                                            vehicle=AccessRequestVehicle()))
        self.assertEqual(3, len(accesses))
        self.assertEqual({"4", "5", "6"}, set([a.id for a in accesses]))

        accesses = self.access_service.find_lpr_accesses(LPRMedium(id="GARIV Q 1"),
                                                         AccessCheckRequest(name=settings.NAME, gate="gate1",
                                                                            vehicle=AccessRequestVehicle()))
        self.assertEqual(1, len(accesses))
        self.assertEqual({"6"}, set([a.id for a in accesses]))

        self.matching_config.edit_distance = 1

        accesses = self.access_service.find_lpr_accesses(LPRMedium(id="B ARIVQ 1"),
                                                         AccessCheckRequest(name=settings.NAME, gate="gate1",
                                                                            vehicle=AccessRequestVehicle()))
        self.assertEqual(7, len(accesses))
        self.assertEqual({"1", "2", "3", "4", "5", "6", "7"}, set([a.id for a in accesses]))

        accesses = self.access_service.find_lpr_accesses(LPRMedium(id="W BRIVQ 1"),
                                                         AccessCheckRequest(name=settings.NAME, gate="gate1",
                                                                            vehicle=AccessRequestVehicle()))
        self.assertEqual(1, len(accesses))
        self.assertEqual({"7"}, set([a.id for a in accesses]))

    def test_find_qr_accesses(self):
        with self.database as db:
            db.add(TestAccessModelBase(id="1", qr_id="QR1", access_infos={}))
            db.add(TestAccessModelBase(id="2", qr_id="QR2", access_infos={}))
            db.add(TestAccessModelBase(id="3", qr_id="QR1", access_infos={}))
            db.add(TestAccessModelBase(id="4", qr_id="NFC1", access_infos={}))

        accesses = self.access_service.find_qr_accesses(Medium(type=MediumType.qr, id="QR1"),
                                                        AccessCheckRequest(name=settings.NAME, gate="gate1",
                                                                           vehicle=AccessRequestVehicle()))
        self.assertEqual(2, len(accesses))
        self.assertEqual("1", accesses[0].id)
        self.assertEqual("3", accesses[1].id)
        self.assertEqual({}, accesses[1].access_infos)
        accesses = self.access_service.find_qr_accesses(Medium(type=MediumType.qr, id="QR3"),
                                                        AccessCheckRequest(name=settings.NAME, gate="gate1",
                                                                           vehicle=AccessRequestVehicle()))
        self.assertEqual(0, len(accesses))

    def test_find_nfc_accesses(self):
        with self.database as db:
            db.add(TestAccessModelBase(id="1", nfc_id="NFC1", access_infos={}))
            db.add(TestAccessModelBase(id="2", nfc_id="NFC2", access_infos={}))
            db.add(TestAccessModelBase(id="3", nfc_id="NFC1", access_infos={}))
            db.add(TestAccessModelBase(id="4", qr_id="QR1", access_infos={}))

        accesses = self.access_service.find_nfc_accesses(Medium(type=MediumType.nfc, id="NFC1"),
                                                         AccessCheckRequest(name=settings.NAME, gate="gate1",
                                                                            vehicle=AccessRequestVehicle()))
        self.assertEqual(2, len(accesses))
        self.assertEqual("1", accesses[0].id)
        self.assertEqual("3", accesses[1].id)
        accesses = self.access_service.find_nfc_accesses(Medium(type=MediumType.nfc, id="NFC3"),
                                                         AccessCheckRequest(name=settings.NAME, gate="gate1",
                                                                            vehicle=AccessRequestVehicle()))
        self.assertEqual(0, len(accesses))

    def test_find_pin_accesses(self):
        with self.database as db:
            db.add(TestAccessModelBase(id="1", pin_id="PIN1", access_infos={}))
            db.add(TestAccessModelBase(id="2", pin_id="PIN2", access_infos={}))
            db.add(TestAccessModelBase(id="3", pin_id="PIN1", access_infos={}))
            db.add(TestAccessModelBase(id="4", qr_id="QR1", access_infos={}))

        accesses = self.access_service.find_pin_accesses(Medium(type=MediumType.pin, id="PIN1"),
                                                         AccessCheckRequest(name=settings.NAME, gate="gate1",
                                                                            vehicle=AccessRequestVehicle()))
        self.assertEqual(2, len(accesses))
        self.assertEqual("1", accesses[0].id)
        self.assertEqual("3", accesses[1].id)
        accesses = self.access_service.find_pin_accesses(Medium(type=MediumType.pin, id="PIN3"),
                                                         AccessCheckRequest(name=settings.NAME, gate="gate1",
                                                                            vehicle=AccessRequestVehicle()))
        self.assertEqual(0, len(accesses))

    def test_find_regex_accesses(self):
        with self.database as db:
            db.add(TestAccessModelBase(id="1", regex="^.+RD$", access_infos={}))
            db.add(TestAccessModelBase(id="2", regex="^BP.+$", access_infos={}))
            db.add(TestAccessModelBase(id="3", regex="^BH.+$", access_infos={}))
            db.add(TestAccessModelBase(id="4", regex="^.+RD$", access_infos={}))
            db.add(TestAccessModelBase(id="5", qr_id="QR1", access_infos={}))

        accesses = self.access_service.find_regex_accesses(LPRMedium(id="BP 123 RD"),
                                                           AccessCheckRequest(name=settings.NAME, gate="gate1",
                                                                              vehicle=AccessRequestVehicle()))
        self.assertEqual(3, len(accesses))
        self.assertEqual("1", accesses[0].id)
        self.assertEqual("2", accesses[1].id)
        self.assertEqual("4", accesses[2].id)
        accesses = self.access_service.find_regex_accesses(LPRMedium(id="G ARIVO 1"),
                                                           AccessCheckRequest(name=settings.NAME, gate="gate1",
                                                                              vehicle=AccessRequestVehicle()))
        self.assertEqual(0, len(accesses))

    def test_deduplicate(self):
        accesses = [AccessCheckAccess(id=str(i), parksettings_id="1", access_data={}, accepted=True,
                                      category=AccessCategory.whitelist, used_medium=Medium(type=MediumType.qr, id=""),
                                      access_infos={}, source="test")
                    for i in [1, 5, 3, 4, 2, 1, 2, 3, 4, 5]]
        accesses = self.access_service.deduplicate_accesses(accesses)
        self.assertEqual(["1", "5", "3", "4", "2"], [a.id for a in accesses])

    def test_gate_check(self):
        def create_access_dummy(id, parksettings_id, category):
            return AccessCheckAccess(id=id, parksettings_id=parksettings_id, access_data={}, accepted=True,
                                     category=category, used_medium=Medium(type=MediumType.qr, id=""), access_infos={},
                                     source="test")

        def create_access_dummies():
            return [create_access_dummy(id="1", parksettings_id=str(uuid.UUID(int=0)),
                                        category=AccessCategory.whitelist),
                    create_access_dummy(id="2", parksettings_id=str(uuid.UUID(int=1)),
                                        category=AccessCategory.whitelist),
                    create_access_dummy(id="6", parksettings_id=None, category=AccessCategory.whitelist),
                    create_access_dummy(id="11", parksettings_id=str(uuid.UUID(int=0)),
                                        category=AccessCategory.shortterm),
                    create_access_dummy(id="12", parksettings_id=str(uuid.UUID(int=1)),
                                        category=AccessCategory.shortterm),
                    create_access_dummy(id="16", parksettings_id=None, category=AccessCategory.shortterm)
                    ]

        self.settings.settings = {("common/gates", ""): {"gate1": Gate(gate="gate1", name="gate1", type=GateType.entry),
                                                         "gate2": Gate(gate="gate2", name="gate2", type=GateType.exit),
                                                         "gate3": Gate(gate="gate3", name="gate3", type=GateType.entry),
                                                         "door": Gate(gate="door", name="door", type=GateType.door)},
                                  ("common/parking_areas2", ""): {},
                                  ("common/parksettings2", ""): {}}

        # test door, all have access
        accesses = create_access_dummies()
        self.access_service.check_accesses_valid_at_gate(accesses, "door")
        self.assertTrue(all(a.accepted for a in accesses))

        # test gate1, parksetting not found, parking_area not found
        accesses = create_access_dummies()
        self.access_service.check_accesses_valid_at_gate(accesses, "gate2")
        self.assertEqual([True] * 3 + [False] * 3, [a.accepted for a in accesses])

        self.settings.settings[("common/parking_areas2", "")] = \
            {str(uuid.UUID(int=0)): ParkingArea(id=str(uuid.UUID(int=0)), name="pa0", gates=["gate1", "gate2"],
                                                shortterm_gates=["gate1"], default_cost_entries=[],
                                                shortterm_limit_type=ShorttermLimitType.no_limit, shortterm_limit=100)}

        # test gate1, parksetting not found, parking_area found and gate is shortterm gate
        accesses = create_access_dummies()
        self.access_service.check_accesses_valid_at_gate(accesses, "gate1")
        self.assertTrue(all(a.accepted for a in accesses))

        # test gate2, parksetting not found, parking_area found and gate is not shortterm gate
        accesses = create_access_dummies()
        self.access_service.check_accesses_valid_at_gate(accesses, "gate2")
        self.assertEqual([True] * 3 + [False] * 3, [a.accepted for a in accesses])

        self.settings.settings[("common/parksettings2", "")] = \
            {str(uuid.UUID(int=0)): Parksetting(id=str(uuid.UUID(int=0)), name="ps0", gates=["gate1"],
                                                default_cost_entries=[]),
             str(uuid.UUID(int=1)): Parksetting(id=str(uuid.UUID(int=1)), name="ps1", gates=["gate2"],
                                                default_cost_entries=[])
             }

        # test gate1, parksetting found, parking_area found and gate is shortterm gate
        # use parksetting also for shortterm if given
        accesses = create_access_dummies()
        self.access_service.check_accesses_valid_at_gate(accesses, "gate1")
        self.assertEqual([True, False, True, True, False, True], [a.accepted for a in accesses])


class RpcTest(AccessServiceWithSessionsTestMixin, RPCServerTestMixin, TestCase):
    rpc_channels = ["access_service"]
    topics = ["access_service", "session", "healthz"]
    access_service_class = TestAccessServiceWithSessions

    def setUp(self):
        super().setUp()
        self.server = RPCServer(context=self.zmq_context())
        self.server.run_as_thread()
        self.access_service.register_rpcs(self.server)
        self.wait_for_rpc_server(self.server)

    def tearDown(self):
        self.server.shutdown()
        super().tearDown()

    def test_access_rpc(self):
        # only test if rpc is passed on to function, function is tested in previous TestCase
        request = AccessCheckRequest(gateway="gate", name=self.core.config.NAME,
                                     vehicle=dict(lpr=dict(id="medium_id", type="lpr")))
        response = self.rpc("access_service", "auth", request, AccessCheckResponse)
        self.assertEqual(True, response.success)
        self.assertIn(request, self.access_service.accessed)

    def test_session_check_in(self):
        self.send_session_start_message()
        self.access_service.wait_for_message_process()
        self.assertEqual(1, len(self.access_service.checked_in))

        MockEvent.reset_all_mocks()
        with self.assertLogs() as cm:
            self.send_session_start_message(gate="error")
            self.access_service.wait_for_message_process()
        self.assertEqual(1, len(self.access_service.checked_in))
        self.assertIn("Error in session check in", cm.output[0])

    def test_session_check_out(self):
        self.send_session_finish_message()
        self.access_service.wait_for_message_process()
        self.assertEqual(1, len(self.access_service.checked_out))

        MockEvent.reset_all_mocks()
        with self.assertLogs() as cm:
            self.send_session_finish_message(gate="error")
            self.access_service.wait_for_message_process()
        self.assertEqual(1, len(self.access_service.checked_out))
        self.assertIn("Error in session check out", cm.output[0])


class AccessTimeTest(TestCase):
    def test_start_end(self):
        now = datetime.utcnow()
        dt = timedelta(days=1)

        at = AccessTime(start=None, end=None)
        self.assertEqual(True, at.is_valid_at(now, "Europe/Vienna"))
        self.assertEqual(True, at.is_valid_at(now + dt, "Europe/Vienna"))
        self.assertEqual(True, at.is_valid_at(now - dt, "Europe/Vienna"))

        at = AccessTime(start=now - dt, end=now + dt)
        self.assertTrue(at.is_valid_at(now, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now - dt, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now + dt, "Europe/Vienna"))
        self.assertFalse(at.is_valid_at(now - 2 * dt, "Europe/Vienna"))
        self.assertFalse(at.is_valid_at(now + 2 * dt, "Europe/Vienna"))

        at = AccessTime(end=now + dt)
        self.assertTrue(at.is_valid_at(now, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now - dt, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now + dt, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now - 2 * dt, "Europe/Vienna"))
        self.assertFalse(at.is_valid_at(now + 2 * dt, "Europe/Vienna"))

        at = AccessTime(start=now - dt)
        self.assertTrue(at.is_valid_at(now, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now - dt, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now + dt, "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(now + 2 * dt, "Europe/Vienna"))
        self.assertFalse(at.is_valid_at(now - 2 * dt, "Europe/Vienna"))

    def test_is_valid_timezone_issue(self):
        at = AccessTime(start="2020-01-01 00:00", end="2020-01-01 04:00")

        with freezegun.freeze_time("2020-01-01 03:30"):
            self.assertTrue(at.is_valid_at(datetime.utcnow(), None))

    def test_is_valid_recurrent_start_end_recurrent(self):
        at = AccessTime(start="2000-01-01T00:00", end="2000-01-07T23:59",
                        recurrence="DTSTART:19990108T110000\nRRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR",
                        duration=3600 * 9)  # from 12:00 to 21:00

        # before the start date
        self.assertFalse(at.is_valid_at(parse("1999-12-30T13:00"), "Europe/Vienna"))  # SA
        self.assertFalse(at.is_valid_at(parse("1999-12-31T13:00"), "Europe/Vienna"))  # FR

        # between start and end
        self.assertFalse(at.is_valid_at(parse("2000-01-01T13:00"), "Europe/Vienna"))  # SA
        self.assertFalse(at.is_valid_at(parse("2000-01-02T13:00"), "Europe/Vienna"))  # SO
        self.assertTrue(at.is_valid_at(parse("2000-01-03T13:00"), "Europe/Vienna"))  # MO
        self.assertTrue(at.is_valid_at(parse("2000-01-04T13:00"), "Europe/Vienna"))  # TU
        self.assertTrue(at.is_valid_at(parse("2000-01-05T13:00"), "Europe/Vienna"))  # WE
        self.assertTrue(at.is_valid_at(parse("2000-01-06T13:00"), "Europe/Vienna"))  # TH
        self.assertTrue(at.is_valid_at(parse("2000-01-07T13:00"), "Europe/Vienna"))  # FR

        # Test the exact limits on friday
        self.assertFalse(at.is_valid_at(parse("2000-01-07T11:59:59+01:00"), "Europe/Vienna"))  # FR
        self.assertTrue(at.is_valid_at(parse("2000-01-07T12:00+01:00"), "Europe/Vienna"))  # FR
        self.assertTrue(at.is_valid_at(parse("2000-01-07T20:59:59+01:00"), "Europe/Vienna"))  # FR
        self.assertFalse(at.is_valid_at(parse("2000-01-07T21:00:00+01:00"), "Europe/Vienna"))  # FR

        # after the end date
        self.assertFalse(at.is_valid_at(parse("2000-01-08T13:00"), "Europe/Vienna"))  # SA
        self.assertFalse(at.is_valid_at(parse("2000-01-09T13:00"), "Europe/Vienna"))  # FR

    def test_is_valid_recurrent_start_no_end_recurrent(self):
        at = AccessTime(start="2000-01-01T00:00", end=None,
                        recurrence="DTSTART:19990108T110000\nRRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR",
                        duration=3600 * 9)  # from 12:00 to 21:00

        # before the start date
        self.assertFalse(at.is_valid_at(parse("1999-12-30T13:00"), "Europe/Vienna"))  # SA
        self.assertFalse(at.is_valid_at(parse("1999-12-31T13:00"), "Europe/Vienna"))  # FR

        # between start and end
        self.assertFalse(at.is_valid_at(parse("2000-01-01T13:00"), "Europe/Vienna"))  # SA
        self.assertFalse(at.is_valid_at(parse("2000-01-02T13:00"), "Europe/Vienna"))  # SO
        self.assertTrue(at.is_valid_at(parse("2000-01-03T13:00"), "Europe/Vienna"))  # MO
        self.assertTrue(at.is_valid_at(parse("2000-01-04T13:00"), "Europe/Vienna"))  # TU
        self.assertTrue(at.is_valid_at(parse("2000-01-05T13:00"), "Europe/Vienna"))  # WE
        self.assertTrue(at.is_valid_at(parse("2000-01-06T13:00"), "Europe/Vienna"))  # TH
        self.assertTrue(at.is_valid_at(parse("2000-01-07T13:00"), "Europe/Vienna"))  # FR

        # years later
        self.assertFalse(at.is_valid_at(parse("2022-01-01T13:00"), "Europe/Vienna"))  # SA
        self.assertFalse(at.is_valid_at(parse("2022-01-02T13:00"), "Europe/Vienna"))  # SO
        self.assertTrue(at.is_valid_at(parse("2022-01-03T13:00"), "Europe/Vienna"))  # MO
        self.assertTrue(at.is_valid_at(parse("2022-01-04T13:00"), "Europe/Vienna"))  # TU
        self.assertTrue(at.is_valid_at(parse("2022-01-05T13:00"), "Europe/Vienna"))  # WE
        self.assertTrue(at.is_valid_at(parse("2022-01-06T13:00"), "Europe/Vienna"))  # TH
        self.assertTrue(at.is_valid_at(parse("2022-01-07T13:00"), "Europe/Vienna"))  # FR

    def test_recurrence_during_dst_change(self):
        at = AccessTime(start="2000-01-01T00:00", end=None, user="test", category="booked-visitor",
                        recurrence="DTSTART:19990108T000000\nRRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR,SA,SU",
                        duration=3600 * 3 + 1)  # from 01:00 to 04:00

        # normal day
        self.assertFalse(at.is_valid_at(parse("2021-03-27T00:00+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-27T01:00+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-27T01:59+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-27T03:00+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-27T04:00+01:00"), "Europe/Vienna"))
        self.assertFalse(at.is_valid_at(parse("2021-03-27T05:00+01:00"), "Europe/Vienna"))  # this is the normal case
        self.assertFalse(at.is_valid_at(parse("2021-03-27T06:00+01:00"), "Europe/Vienna"))

        # from +01:00 to +02:00
        self.assertFalse(at.is_valid_at(parse("2021-03-28T00:00+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-28T01:00+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-28T01:59+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-28T03:00+02:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-03-28T04:00+02:00"), "Europe/Vienna"))
        # usually it goes only until 4 o'clock, but during dst change we add the hour to avoid conflicts
        self.assertTrue(at.is_valid_at(parse("2021-03-28T05:00+02:00"), "Europe/Vienna"))  # special case
        self.assertFalse(at.is_valid_at(parse("2021-03-28T06:00+02:00"), "Europe/Vienna"))

        # from +02:00 to +01:00
        self.assertFalse(at.is_valid_at(parse("2021-10-31T00:00+02:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-10-31T01:00+02:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-10-31T01:59+02:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-10-31T03:00+01:00"), "Europe/Vienna"))
        self.assertTrue(at.is_valid_at(parse("2021-10-31T04:00+01:00"), "Europe/Vienna"))
        # usually it goes only until 4 o'clock, but during dst change we add the hour to avoid conflicts
        self.assertTrue(at.is_valid_at(parse("2021-10-31T05:00+01:00"), "Europe/Vienna"))  # special case
        self.assertFalse(at.is_valid_at(parse("2021-10-31T06:00+01:00"), "Europe/Vienna"))
