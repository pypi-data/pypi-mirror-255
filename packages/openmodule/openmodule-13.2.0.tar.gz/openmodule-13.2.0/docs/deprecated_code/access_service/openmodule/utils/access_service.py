import logging
import re
from typing import Union, List, Type, Dict, Optional, Any

import editdistance
from settings_models.settings.common import ParkingAreas, Parksettings, Gates, GateType
from sqlalchemy import Column, Integer, String, event
from sqlalchemy.ext.hybrid import hybrid_property

from openmodule.config import settings
from openmodule.core import core
from openmodule.database.custom_types import JSONEncodedDict
from openmodule.database.database import Database
from openmodule.models.access_service import SessionStartMessage, \
    SessionFinishMessage, SessionDeleteMessage, SessionExitWithoutEntryMessage, SessionIncompleteMessage, \
    AccessCheckRequest, AccessCheckResponse, AccessCheckAccess, AccessCheckRejectReason, AccessCategory
from openmodule.models.vehicle import LPRMedium, Medium, QRMedium, MediumType
from openmodule.rpc.server import RPCServer
from openmodule.utils.charset import CharsetConverter, legacy_lpr_charset
from openmodule.utils.kv_store import KVStore, KVEntry
from openmodule.utils.matching import PlateYamlSelector, MatchingConfig
from openmodule.utils.settings import SettingsProvider


class AccessModelBase(KVEntry):
    # so key can also be accessed as id
    @hybrid_property
    def id(self):
        return self.key

    @id.setter
    def id(self, email):
        self.key = email

    # ids for open session service
    customer_id = Column(String, nullable=True)        # id used by open session service (customer id)
    car_id = Column(String, nullable=True)        # id used by open session service (customer car id)
    group_id = Column(String, nullable=True)                # id by open session service (contract id)

    access_infos = Column(JSONEncodedDict, nullable=True)  # infos attached to all messages, null is empty dict

    # lpr with matching config
    lpr_id = Column(String, nullable=True)
    lpr_id_search = Column(String, nullable=True, index=True)
    lpr_country = Column(String, nullable=True)
    matching_scheme = Column(String, nullable=True)
    matching_version = Column(Integer, nullable=True)

    # other media
    qr_id = Column(String, nullable=True, index=True)
    nfc_id = Column(String, nullable=True, index=True)
    pin_id = Column(String, nullable=True, index=True)
    regex = Column(String, nullable=True, index=True)

    @classmethod
    def parse_value(cls, value) -> dict:
        """Parses the value from the server into a dict of {column-name: value}"""
        raise NotImplementedError


lpr_search_converter = CharsetConverter(legacy_lpr_charset)


@event.listens_for(AccessModelBase, "before_update", propagate=True)
@event.listens_for(AccessModelBase, "before_insert", propagate=True)
def before_insert_and_update(_, __, target: AccessModelBase):
    if target.lpr_id:
        target.lpr_id_search = lpr_search_converter.clean(target.lpr_id)

    if (target.lpr_id is None) != (target.lpr_country is None):
        raise ValueError("field `lpr_country` must also be set iff `lpr_id` is set.")

    if not any([target.lpr_id, target. qr_id, target.nfc_id, target.pin_id, target.regex]):
        raise ValueError("No id or regex set in access")


class AccessService:
    """
    AccessService template class
    provides basic functionality used for backups
    * subscribes to AccessServiceMessages and automatically registers AccessService
    * subscribes to CountMessages and calls check_in/check_out correspondingly
    * provides method for the AccessService / auth rpc with the check_access_service_access method

    """

    auth_request_request_model = None

    def __init__(self):
        self.log = logging.getLogger()

    def register_rpcs(self, rpc_server: RPCServer):
        rpc_server.add_filter(self._access_service_filter, "access_service", "auth")
        assert self.auth_request_request_model, "You need to set the auth_request_request_model for the access service"
        rpc_server.register_handler("access_service", "auth", request_class=self.auth_request_request_model,
                                    response_class=AccessCheckResponse, handler=self.rpc_check_access)

    def _access_service_filter(self, request, message, handler) -> bool:
        access_service = request.name
        if not access_service:
            return False
        return settings.NAME == access_service

    def rpc_check_access(self, request: AccessCheckRequest, _) -> AccessCheckResponse:
        """
        Check if the user has access at the given gate at the given time according to DEV-A-916
        """

        raise NotImplementedError()


class AccessServiceWithSessions(AccessService):
    def __init__(self):
        super().__init__()
        core().messages.register_handler("session", SessionStartMessage, self.handle_session_start_message)
        core().messages.register_handler("session", SessionFinishMessage, self.handle_session_finish_message)
        core().messages.register_handler("session", SessionDeleteMessage, self.handle_session_delete_message)
        core().messages.register_handler("session", SessionExitWithoutEntryMessage,
                                         self.handle_session_exit_without_entry_message)
        core().messages.register_handler("session", SessionIncompleteMessage,
                                         self.handle_session_incomplete_message)

    def check_in_session(self, message: SessionStartMessage):
        """
       this method should check in the user of the message in the AccessService
        it should raise an Exception if it fails
       :param message: SessionStartMessage
       """
        raise NotImplementedError()

    def check_out_session(self, message: SessionFinishMessage):
        """
        this method should check out the user of the message of the AccessService
        :param message: SessionFinishMessage
        """
        raise NotImplementedError()

    def session_error_message(self, message: Union[SessionDeleteMessage, SessionIncompleteMessage,
                                                   SessionExitWithoutEntryMessage]):
        """
               this method should handle all possible session errors
               :param message: Session error message
               """
        raise NotImplementedError()

    def handle_session_start_message(self, message: SessionStartMessage):
        """
        Checks the user in with the data of the session start message
        """
        self.log.debug(f"received a session check in message for access {message.access_id}")
        try:
            self.check_in_session(message)
        except Exception as e:
            data = message.dict()
            data.pop("name", None)
            self.log.exception(f"Error in session check in for access {message.access_id}", extra=data)

    def handle_session_finish_message(self, message: SessionFinishMessage):
        """
        Checks the user out with the data of the session finish message
        """
        self.log.debug(f"received a session check out message for access {message.access_id}")
        try:
            self.check_out_session(message)
        except Exception as e:
            data = message.dict()
            data.pop("name", None)
            self.log.exception(f"Error in session check out for access {message.access_id}", extra=data)

    def handle_session_delete_message(self, message: SessionDeleteMessage):
        """
        Handles the session delete message
        """

        self.log.debug(f"received a session delete message for access {message.access_id}")
        try:
            self.session_error_message(message)
        except Exception as e:
            data = message.dict()
            data.pop("name")
            self.log.exception(f"Error in session delete for access {message.access_id}", extra=data)

    def handle_session_exit_without_entry_message(self, message: SessionExitWithoutEntryMessage):
        """
        Handles the session exit_without_entry message
        """

        self.log.debug(f"received a session exit_without_entry message for access {message.access_id}")
        try:
            self.session_error_message(message)
        except Exception as e:
            data = message.dict()
            data.pop("name", None)
            self.log.exception(f"Error in session exit_without_entry message for access {message.access_id}",
                               extra=data)

    def handle_session_incomplete_message(self, message: SessionIncompleteMessage):
        """
        Handles the session incomplete message
        """

        self.log.debug(f"received a session incomplete message for access {message.access_id}")
        try:
            self.session_error_message(message)
        except Exception as e:
            data = message.dict()
            data.pop("name", None)
            self.log.exception(f"Error in session incomplete message for access {message.access_id}", extra=data)

    def rpc_check_access(self, request: AccessCheckRequest, _) -> AccessCheckResponse:
        """
        Check if the user has access at the given gate at the given time according to DEV-A-916
        """

        raise NotImplementedError()


class AccessServiceWithDatabase(AccessService, KVStore):
    """
    Base class for Access Services which hold their accesses in a database
    The KVStore has to be instantiated separately
    """
    database_table: Type[AccessModelBase]

    def __init__(self, database: Database, matching_config: MatchingConfig,
                 settings_provider: Optional[SettingsProvider] = None, sync_timeout: float = 300.0):
        AccessService.__init__(self)
        KVStore.__init__(self, database, sync_timeout=sync_timeout)
        self.matching_config = matching_config
        self.settings = settings_provider or SettingsProvider()

    def register_rpcs(self, rpc_server: RPCServer) -> None:
        AccessService.register_rpcs(self, rpc_server)
        KVStore.register_rpcs(self, rpc_server)

    def rpc_check_access(self, request: AccessCheckRequest, _) -> AccessCheckResponse:
        """
        Check if the user has access at the given gate at the given time according to DEV-A-916
        """

        raise NotImplementedError()

    def db_model_to_access(self, db_model: KVEntry, used_medium: Medium, request: AccessCheckRequest) \
            -> AccessCheckAccess:
        """
        converts the database model to an access
        """
        raise NotImplementedError

    def _find_lpr_accesses_ed0(self, db, medium: LPRMedium):
        plate_clean = lpr_search_converter.clean(medium.id)
        accesses = db.query(self.database_table).filter(self.database_table.lpr_id_search == plate_clean).all()
        if not accesses:
            return []

        session_plate_db = {}
        plates = PlateYamlSelector.from_config(self.matching_config)
        for access in accesses:
            plates.insert_into_db_and_create_record(
                session_plate_db, access.lpr_id, access.lpr_country,
                access.matching_scheme or self.matching_config.default_scheme,
                access.matching_version if access.matching_version is not None
                else self.matching_config.default_version,
                access_id=access.id)
        to_match = plates.create_plate_for_matching(medium.id, medium.country.code, medium.confidence,
                                                    medium.country.confidence, medium.alternatives)
        matches = plates.match_plate(to_match, session_plate_db,
                                     use_alternatives=self.matching_config.use_alternatives, max_ed=0,
                                     return_only_best=False)
        match_access_ids = sum([[o["access_id"] for o in eds] for eds in matches], [])
        return [access for access in accesses if access.id in match_access_ids]

    def _find_lpr_accesses_edX(self, db, medium: LPRMedium, edit_distance: int):
        lpr_accesses = db.query(self.database_table).filter(self.database_table.lpr_id_search.isnot(None)).all()
        return [access for access in lpr_accesses
                if editdistance.eval(access.lpr_id_search, lpr_search_converter.clean(medium.id)) <= edit_distance]

    def find_lpr_accesses(self, medium: LPRMedium, request: AccessCheckRequest) -> List[AccessCheckAccess]:
        with self.db as db:
            if self.matching_config.edit_distance > 0:
                accesses = self._find_lpr_accesses_edX(db, medium, self.matching_config.edit_distance)
            else:
                accesses = self._find_lpr_accesses_ed0(db, medium)
            return [self.db_model_to_access(access, LPRMedium(id=access.lpr_id), request)
                    for access in accesses]

    def find_qr_accesses(self, medium: Medium, request: AccessCheckRequest) -> List[AccessCheckAccess]:
        with self.db as db:
            return [self.db_model_to_access(access, QRMedium(id=access.qr_id), request)
                    for access in db.query(self.database_table).filter(self.database_table.qr_id == medium.id).all()]

    def find_nfc_accesses(self, medium: Medium, request: AccessCheckRequest) -> List[AccessCheckAccess]:
        with self.db as db:
            return [self.db_model_to_access(access, Medium(type=MediumType.nfc, id=access.nfc_id), request)
                    for access in db.query(self.database_table).filter(self.database_table.nfc_id == medium.id).all()]

    def find_pin_accesses(self, medium: Medium, request: AccessCheckRequest) -> List[AccessCheckAccess]:
        with self.db as db:
            return [self.db_model_to_access(access, Medium(type=MediumType.pin, id=access.pin_id), request)
                    for access in db.query(self.database_table).filter(self.database_table.pin_id == medium.id).all()]

    def find_regex_accesses(self, medium: LPRMedium, request: AccessCheckRequest) -> List[AccessCheckAccess]:
        with self.db as db:
            regex_accesses = db.query(self.database_table).filter(self.database_table.regex.isnot(None)).all()
            return [self.db_model_to_access(access, Medium(type=MediumType.regex, id=access.regex), request)
                    for access in regex_accesses if re.match(access.regex, medium.id)]

    def deduplicate_accesses(self, accesses: List[AccessCheckAccess]):
        res = []
        ids = set()
        for access in accesses:
            if access.id not in ids:
                res.append(access)
                ids.add(access.id)
        return res

    def check_accesses_valid_at_gate(self, accesses: List[AccessCheckAccess], gate: str):
        gates = self.settings.get("common/gates")
        parking_areas = self.settings.get("common/parking_areas2")
        parksettings = self.settings.get("common/parksettings2")

        not_found_parksettings = []
        if gates.get(gate) and gates.get(gate).type == GateType.door:
            return  # no check necessary for doors

        for access in accesses:
            parksetting = parksettings.get(access.parksettings_id)  # same behavior for parksetting None and not found
            if parksetting is None and access.parksettings_id is not None:
                not_found_parksettings.append(access.parksettings_id)

            if parksetting is None and access.category in [AccessCategory.shortterm, AccessCategory.unknown]:
                # treat like unknown shortterm parker -> check if gate is a shortterm gate
                if all(gate not in pa.shortterm_gates for pa in parking_areas.values()):
                    access.accepted = False
                    access.reject_reason = AccessCheckRejectReason.wrong_gate
            elif parksetting is None:
                pass  # no check necessary because access on all gates
            else:
                if access.category == AccessCategory.unknown:
                    self.log.error("Parksetting not None for access of category unknown. This is an invalid access")
                # TODO: Comment in next two lines when all access sources are fully changed to new parksettings
                # elif access.category == AccessCategory.shortterm:
                #     self.log.error("Parksetting not None for access of category shortterm. This is an invalid access")
                # only check if parksetting_id is not None (None means any gate is ok)
                if gate not in parksetting.gates:
                    access.accepted = False
                    access.reject_reason = AccessCheckRejectReason.wrong_gate
        if not_found_parksettings:
            self.log.warning(f"Some parksettings set in access were not found in settings: {not_found_parksettings}")

    def shutdown(self, timeout=10):
        KVStore.shutdown(self, timeout=timeout)
