# Database

[TOC]

On the device we use `sqlalchemy` for our database, additionally we use `alembic` for our migrations. An example of a
database is included in openmodule-test.

## Models

### Definition

All database models inherit a `Base` from `sqlalchemy` and need an unique id.

```python
import uuid
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DatabaseTestModel(Base):
    __tablename__ = "test"
    id = Column(String, default=lambda: str(uuid.uuid4()), unique=True, primary_key=True)
    value = Column(Integer, default=1)
    string = Column(String, default="initial")
```

### Registration

#### Models

All database models you want to use need to registered. This happens in the `src/database/alembic/env.py` file. Simply
list all used Bases in the register_bases function.

```python
from database.database_models import Base
from somewhere import Base as some_base

register_bases([Base, some_base])
```

#### Custom Column Types

You can also define custom column types, but they must inherit CustomType from `openmodule.database.custom_types` or
else there will be import errors in the migrations

```python
class TZDateTime(CustomType):
    impl = DateTime

    def process_bind_param(self, value, dialect):
        if value is not None:
            assert value.tzinfo is None, "You need to convert a datetime to a naive time, because sqlite loses tz infos"
        return value
```

## Migrations

### Generating migrations

To generate the migration use the provided script `src/database/makemigration.sh` with a name for your migration.

```shell script
./makemigrations -m <name>
```

Afterwards the migrations are created under `src/database/alembic/versions`.

### How to migrate

The database is always automatically migrated on creation of any database object in the program.

**ℹ Information:** Before a migration upgrade is executed a backup of the current database is created.

The backup file is stored in the database folder and is named `{service-name}_YYYYmmddHHMMSS.sqlite3.backup`.
Example: "om_showcase_example_1_20240125123456.sqlite3.backup"

### Migration Examples

The alembic documentation already has some migration examples and tutorials, but here are some quick tips and pitfalls
we have encountered.

**⚠ Renaming Columns**

When you rename a column, alembic usually creates a new column and drops the old one. It does not know whether you
actually want a new
column or want to rename the old one. This is why for renaming you usually have to write your own migration instead of
auto generating it.

```python
# correct way: renames the column, keeps the data
def upgrade():
    op.pre_upgrade()

    with op.batch_alter_table('my_table_name', schema=None) as batch_op:
        batch_op.alter_column("old_column", new_column_name="new_column")

    op.post_upgrade()
```

The wrong (auto-generated) migration would look like this. In the best case it would result in a null constraint error,
but in the worst
case it would leave a empty column behind with all null values and you never notice until its too late.

```python
# WRONG WAY! drops the column, deletes the data and creates a new empty column
def upgrade():
    op.pre_upgrade()

    with op.batch_alter_table('my_table_name', schema=None) as batch_op:
        batch_op.add_column(sa.Column('new_column', sa.Integer(), nullable=True))
        batch_op.drop_column('old_column')

    op.post_upgrade()
```

### Avoiding broken database after failed migration

A failed migration might lead to a broken state where no migration is possible anymore. To avoid / fix this the
op.pre_upgrade() operation deletes all temporary tables from alembic. Intern the op.pre_upgrade()
calls `openmodule.database.drop_alembic_tmp_tables`

```python
def upgrade():
    op.prep_upgrade()
    ${upgrades if upgrades else "pass"}
```

### Foreign key constraints during migrations

Foreign key constraints are disabled during migrations, meaning you could possibly end up with rows referencing a
non-existing row. This only happens if manually written code messes this up. Alembic's operations should not cause such
a state, but due to limitations in sqlite foreign key constraints are disabled during migrations, because they cannot be
turned back on in the middle of a migration.

Foreign key constraints are disabled during `op.pre_upgrade()`.

## Database Access

To access the database we have to create our own instance, you can also pass the parameter `database=True` to the core
for it to create a database:
Then we can create a session an access the database.

```python
database = Database(**kwargs)
with database as db:
    do_stuff(db, ...)
```

If an exception is raised during an open database session, all changes will be rolled back.  
It is also possible to create multiple database within a program, but the need to is quite questionable.

## Basic database operations

Normally sqlalchemy functions should suffice for most jobs. We implemented some additional functionality as functions
under `openmodule.utils.db_helper`.

### Create

* db.add(model: DatabaseModel)
* db.add_all(models: List[DatabaseModel])

### Query

* base_query = db.query(DatabaseModel)
* query = base_query..filter_by(**kwargs)
* query.all() returns a list

### Query results

* instance = query.one() -> returns element or raises exception if query has more or no elements (MultipleResultsFound,
  NoResultFound)
* instance = query.first() -> returns first element of query or None
* query.all() -> return all elements of object
* query.one() -> returns one element or raises exception if no elements
* query.one_or_none() -> returns first element or None if no elements, but raises an exception if multiple elements
* query.get() -> query object with primary key, returns None if not found
* query.count() -> returns number of elements in query

### Update

* db.add(model: DatabaseModel) -> previously created model
* db_helper.update_query(db, query, values: dict)

### Delete

* db.delete(model: DatabaseModel)
* db_helper.delete_query(db, query)

### Useful query functions

* order_by(*args) -> ordering
* yield_by(int) -> for batch processing
* distinct(*args) -> distinct

# Key-Value Store

The key-value store `openmodule.utils.kv_store.KVStore` interacts with the database to create a key-value store that is
kept in
sync with an external Server (RPC Server). **Services must not create/edit/delete the key-value entries themselves.
They must only be created/edited/deleted by the provided rpcs that are called by the server.** (`channel=kv_store`).
The database model needs to be created by the service by inheriting from the `openmodule.utils.kv_store.KVEntry`.

### KVStoreHandler

Every `KVStore` has to be registered with the `KVStoreHandler` class. This class is responsible for syncing the
`KVEntry`s on startup and reconnect.
The `KVStoreHandler` implements only the sync and uses underlying methods of the `KVStore` for the actual syncing.

#### Syncing

The `run()` method of the `KVStoreHandler` handles the syncing and you only have to provide all relevant
`KVStore`s.

#### Example on how to register a `KVStore` with the `KVStoreHandler`

```python
from openmodule.core import core
from openmodule.utils.kv_store import KVStoreHandler
from openmodule.utils.kv_store import KVStore


class ExampleKVStore(KVStore):
    database_table = ExampleKVEntry


kv_handler = KVStoreHandler(core().database, core().rpc_client, ExampleKVStore)
# or you can use the `add_kvstore()` method
kv_handler.add_kvstore(ExampleKVStore2)
```

### KVEntry

* Must be inherited
* `key` and `e_tag` columns must not be changed
* Additional columns should be created.
* The `parse_value(value: dict) -> List[Base]` method needs to be implemented.
    * It is called when a before a new entry is created.
    * Should parse the value (as sent by the external source) into a list of database instances.
    * Returns a list of database instances that could be mixed, but at least 1 instance must be returned.

### Notification on entry changed

* Inherit from `KVStoreWithChangedNotification`
* Implement `_get_comparison_values` and `_send_changed_notification` (needs check for if changed, most likely use
  `_find_changed_kvs`)
* Implement a meaningful `comparison_value` function for your Database Model
