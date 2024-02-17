# Openmodule Coding Standard

[TOC]

## Models

* All Messages or RPC requests MUST be defined as pydantic models in either `openmodule/models` or in `src/models` to
  avoid confusion about datatypes.

* All Models MUST be must inherit `OpenModuleModel` or one of its children

* ZMQ Messages MUST inherit `ZMQMessage`

### Enum

As a coding standard we are using camel case and the name of the enum and value should always be the same.
This means you are not allowed to use a dash (`-`) in the enum value.

We are also using the `str` type for all enums, because we want to compare the enum value against strings.

```python
from enum import Enum


class MyStatus(str, Enum):
    very_good = "very_good"
    good = "good"
    this_is_fine = "this_is_fine"
    something_is_wrong = "something_is_wrong"
```

## Database

* All database models must be defined within either `openmodule/models` or in the directory `src/database`

* All database model names have to end with Model, i.e. TestModel(Base)

* All database interactions MUST be defined in functions under `src/database/database.py`. There are no other access of
  the database in any other file.

* All functions in `src/database/database.py` MUST have the database/session as first parameter: `def stuff(db, ...)`

* All table names MUST use "_" as separator

* For single object queries only use `query.one()` and `query.first()`

## Typing

We use type annotation for functions and variables.
This not only improves read ability of the source code, but the IDEs and linters can
also use this information to provide better code completion and error checking.

### Examples

```python
class MyPriceModel(OpenModuleModel):
    price: float  # net price
    currency: str  # currency
    vat: float = 0  # amount of vat for country


vat_country_in_percent: float = 20.0
my_products: Dict[str, MyPriceModel] = {"apple": MyPriceModel(price=1.0, currency="EUR")}


def calculate_vat(price: MyPriceModel) -> float:
    """Calculate the vat for a product."""
    return price.price * vat_country_in_percent / 100.0
```


We allow that function that are not returning anything to not have a return type annotation.

```python
def updating_vat(products: Dict[str, MyPriceModel]):
    """We are directly updating the vat in the products, therefore we have no return value."""
    for product in products.values():
        product.vat = product.price * vat_country_in_percent / 100.0
```
