# Access Service

[TOC]

Inherit from either

* Access Service: No session handling and no access sync
* AccessServiceWithSessions: Session handling (check in, check out, errors) and no access sync

The Access Service module also provides some functions, that are commonly used by the Access Service implementations

* `get_lpr_id_search`: Is used to convert the given license plate to our license plate search structure
* `deduplicate_accesses`: Can be used to make sure, that no duplicates are in the return value of the `AccessCheckResponse`
* `find_lpr_accesses`: Returns the correct accesses for the license plates, that matched via our Matching Config
* `check_accesses_valid_at_gate`: Marks accesses invalid if e.g. the accesses does not have the current gate in their
  parksetting

For a more detailed guide set the [Access Service Documentation](https://youtrack.acc.si/articles/DEV-A-1187/).

## Access Service

You have to implement the `rpc_check_access` function and probably add some other custom stuff.

An example implementations is shown below.


```python
def rpc_check_access(self, request: AccessCheckRequest, _) -> AccessCheckResponse:
    """
    Check if the user has access at the given gate at the given time according to DEV-A-916
    """
    self.log.debug(f"Check Access for {request.vehicle} at gate {request.gate}")

    accesses = []
    if request.vehicle.lpr:
        accesses += self.find_lpr_accesses(request.vehicle.lpr)
        accesses += self.find_regex_accesses(request.vehicle.lpr)
    if request.vehicle.qr:
        accesses += self.find_qr_accesses(request.vehicle.qr)

    accesses = deduplicate_accesses(accesses)

    # we mark the access invalid, if the access is currently not valid or the gate is incorrect for the access
    check_accesses_valid_at_time(accesses, request.timestamp)
    if request.gate:
        check_accesses_valid_at_gate(accesses, request.gate, self.settings)

    self.log.info(f"Found {len(accesses)} matching accesses "
                  f"where {len([a for a in accesses if a.accepted])} are valid")
    return AccessCheckResponse(success=True, accesses=accesses, readable_service_name=_("Test Access Service"))
```

### Access Service Reject Reasons

In the enum `AccessCheckRejectReason` common reject reasons can be found.

#### Reject Reason "wrong_gate"

This reject reason is automatically set if the function `check_accesses_valid_at_gate()` is used.

#### Reject Reason "wrong_time"

If your access service has some time restriction the reject reason `wrong_time` can be returned.
**Do not** use this for accesses with start and end (e.g. permanent access for a month)
as these accesses should be ignored if outside start and end.

#### Reject Reason "custom"

If the given e.g. license plate should be rejected for a specific other reason the value `custom` should
be used. If the reject reason `custom` is used then the string field `supplementary_infos` has to be set!

## AccessServiceWithSessions

In addition to the Access Service stuff implement the session handling functions `check_in_session`, `check_out_session`
and `check_out_session`

## AccessService and KVStore

A running version of the Python snippets can be found in the [Test Cases](../tests/test_utils_access_service.py) file.

An Access Service often has some kind of database where the parking permissions are saved. For saving a parking
permission into a local database the KVStore can be used.

First you have to create your own database model that inherits from `KVEntry`.

```python
class TestAccessModelBase(Base, KVEntry):
    __test__ = False
    __tablename__ = "test_access_model"

    # the KVEntry uses the field `key` as primary key, but we prefer our normal primary key 'id'
    @hybrid_property
    def id(self):
        return self.key

    @id.setter
    def id(self, value):
        self.key = value

    # ids for open session service
    customer_id = Column(String, nullable=True)  # id used by open session service (customer id)
    car_id = Column(String, nullable=True)  # id used by open session service (customer car id)
    group_id = Column(String, nullable=True)  # id by open session service (contract id)

    parksettings_id = Column(String, nullable=True)  # None is allowed for simplicity as only gates are necessary

    access_infos = Column(JSONEncodedDict, nullable=True)  # infos attached to all messages, null is empty dict

    # lpr with matching config
    lpr_id = Column(String, nullable=True)
    lpr_id_search = Column(String, nullable=True, index=True)
    lpr_country = Column(String, nullable=True)
    matching_scheme = Column(String, nullable=True)
    matching_version = Column(Integer, nullable=True)

    # other media
    qr_id = Column(String, nullable=True, index=True)
    regex = Column(String, nullable=True, index=True)

    @classmethod
    def parse_value(cls, value: dict) -> List['TestAccessModelBase']:
        return [cls(**value)]


# this is just a convenience method that patches lpr_id_search,
# so that I don't need to set the lpr_id_search explicit on model creation
@event.listens_for(TestAccessModelBase, "before_update", propagate=True)
@event.listens_for(TestAccessModelBase, "before_insert", propagate=True)
def before_insert_and_update(_, __, target: TestAccessModelBase):
    if target.lpr_id:
        target.lpr_id_search = get_lpr_id_search(target.lpr_id)

    if (target.lpr_id is None) != (target.lpr_country is None):
        raise ValueError("field `lpr_country` must also be set iff `lpr_id` is set.")

    if not any([target.lpr_id, target.qr_id, target.regex]):
        raise ValueError("No id or regex set in access")
```

You have to manually implement the `parse_value` method, that parses the value from the server into kwargs for the
KVEntry constructor. In this method you have to manually convert the field values to the correct database types.
For example, you have to convert the `datetime` string to a `datetime` object.


After our local database is defined. We can create our KVStore, that will handle the KV sync for us.
More information about the KVStore can be found [database documentation](database.md) in the section "Key-Value Store".
Every KVStore has to be added to our `KVStoreHandler`. This handler class will provide a `run()` method.

```python
from openmodule.core import core
from openmodule.utils.kv_store import KVStore, KVStoreHandler

class AccessKVStoreExample(KVStore):
    database_table = TestAccessModelBase

kvstore_handler = KVStoreHandler(core().database, core().rpc_client, AccessKVStoreExample)
kvstore_handler.add_kvstore(rpc_server)
kvstore_handler.run()
```

The KVStore provides a hook method `parse()`, that can be used to generate more local database models, from the
KV data. In the section "Multiple KVStore" section below you can find an example, how to use this
hook.

At last, we have to implement the `rpc_check_access` method.

## Multiple KVStore

A running version of the Python snippets can be found in the [Test Cases](../tests/test_utils_kv_store_multiple.py)
file.

Every KVStore has to have the parameter `suffix` set. This suffix is used as an identifier for the KV sync channel.

First we define our local database structure as we would normally do.

```python
class CarData(pydantic.BaseModel):
    license_plate: str
    country: str
    customer_car_id: Optional[str]
    matching_scheme: Optional[str]
    matching_version: Optional[int]


class Contract(Base, KVEntry):
    __tablename__ = "contracts"

    # because the primary key of the KV entry is named 'key' we provide getter and setter for our preferred name 'id'
    @hybrid_property
    def id(self):
        return self.key

    @id.setter
    def id(self, value):
        self.key = value

    contract_id = Column(String, nullable=False)  # group id for controller
    group_limit = Column(Integer, nullable=True)
    access_infos = Column(JSONEncodedDict, nullable=True)
    barcode = Column(String, nullable=True)  # qrcode

    # 1 to many relationship to our license plate table
    # relationship to child tables with cascade delete that deletes orphaned entries as well
    # this relationship is needed for correct deletion of the additional tables
    cars: List['Car'] = relationship("Car", back_populates="contract", cascade="all, delete", passive_deletes=True)

    @classmethod
    def parse_value(cls, value: dict) -> List[Union['Contract', 'Car']]:
        # we validate cars json payload here with Pydantic model parse_obj_as() function
        instances = []
        barcode = value.get("barcode")
        cars_data = value.get("cars")
        assert barcode or cars_data, "Either a barcode or cars must be present"
        contract = Contract(contract_id=value.get("contract_id"), group_limit=value.get("group_limit"),
                            access_infos=value.get("access_infos"), barcode=barcode)
        if cars_data is not None:
            # validate car json payload with Pydantic model
            cars_data = pydantic.parse_obj_as(List[CarData], cars_data)
            for c in cars_data:
                # you have to manually set the lpr_search_id with the clean function
                car = Car(contract=contract, lpr_id=c.license_plate,
                          lpr_search_id=access_utils.get_lpr_id_search(c.license_plate),
                          lpr_country=c.country, customer_car_id=c.customer_car_id,
                          matching_scheme=c.matching_scheme, matching_version=c.matching_version)
                instances.append(car)
        instances.append(contract)
        return instances


class Reservation(Base, KVEntry):
    __tablename__ = "reservations"

    # because the primary key of the KV entry is named 'key' we provide getter and setter for our preferred name 'id'
    @hybrid_property
    def id(self):
        return self.key

    @id.setter
    def id(self, value):
        self.key = value

    # a reservation has a start and an end date
    start = Column(TZDateTime, nullable=False)
    end = Column(TZDateTime, nullable=False)
    barcode = Column(String, nullable=False)  # qrcode

    # 1 to 1 relationship to our car table
    car: 'Car' = relationship("Car", back_populates="reservation", cascade="all, delete", passive_deletes=True,
                              uselist=False)

    @classmethod
    def parse_value(cls, value: dict) -> List[Union['Reservation', 'Car']]:
        # this method has to be implemented by the child class, and therefore we validate car json payload here
        # with Pydantic model parse_obj() method
        instances = []
        start = datetime.datetime.fromisoformat(value["start"]) if value.get("start") else None
        end = datetime.datetime.fromisoformat(value["end"]) if value.get("end") else None
        reservation = Reservation(start=start, end=end, barcode=value.get("barcode"))
        car_data = value.pop("car", None)
        if car_data:
            car_data = CarData.parse_obj(car_data)
            car = Car(reservation=reservation, lpr_id=car_data.license_plate,
                      lpr_search_id=access_utils.get_lpr_id_search(car_data.license_plate),
                      lpr_country=car_data.country, customer_car_id=car_data.customer_car_id,
                      matching_scheme=car_data.matching_scheme, matching_version=car_data.matching_version)
            instances.append(car)
        instances.append(reservation)
        return instances


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lpr_id = Column(String, nullable=False)
    lpr_search_id = Column(String, nullable=False, index=True)
    lpr_country = Column(String, nullable=False)
    customer_car_id = Column(String, nullable=True)
    matching_scheme = Column(String, nullable=True)
    matching_version = Column(Integer, nullable=True)

    # foreign keys to parent table - BEWARE contracts.id is just a wrapper in python!
    contract_id = Column(String, ForeignKey("contracts.key", ondelete="CASCADE"), nullable=True)
    contract = relationship("Contract", back_populates="cars")
    reservation_id = Column(String, ForeignKey("reservations.key", ondelete="CASCADE"), nullable=True)
    reservation = relationship("Reservation", back_populates="car")
```

In the above example we define a 1 to many relations ship for `Contract` and `Car`
and a 1 to 1 relationship for `Reservation` and `Car`.
To implement this relationship we have to add a foreign key to the child table and a relationship to the parent table.

In the `parse_value` method we have to manually parse the incoming data from the server into our database model.
In this method we use the [Pydantic](https://docs.pydantic.dev/latest/) model to verify the incoming nested data.
With the method `parse_value()` we can represent the local database structure as we want.
The `parse_value()` method can return any object that inherits from a database model. This means you can return a list
of mixed objects. But at least one of the returned objects has to be an instance of the `database_table` class.


We define our KVStores with their database table and the suffix.

```python
class KVStoreContracts(KVStore):
    database_table = Contract
    # the suffix identifies our KV store sync channel
    suffix = "contract"


class KVStoreReservations(KVStore):
    database_table = Reservation
    suffix = "reservation"
```

Now we almost finished. We have to create our `KVStoreHandler` instance and register our KVStores.

```python
multi_store = KVStoreHandler(core().database, core().rpc_client, KVStoreContracts, KVStoreReservations)
multi_store.register_rpcs(self.rpc_server)
multi_store.run()
```

Now you can implement your Access Service with your chosen local database structure.
