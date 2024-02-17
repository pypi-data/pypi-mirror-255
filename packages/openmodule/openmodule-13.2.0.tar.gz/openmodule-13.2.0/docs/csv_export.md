# CSV Exporter

[TOC]

The file `utils/csv_export.py` contains a `render` function that can be used to export a list of objects or dicts to a 
csv file. 
Important specifications of the generated csv file:
* encoding "utf-16-le"
* `csv.QUOTE_ALL` setting 
* "," as comma for floats. 
* delimiter is `"\t"` 
* line terminator is `"\r\n"`. 

** ⚠ Important:** `None` values are converted to empty strings.

## Usage

The render function takes the following arguments:
* `file_object`: A file object to which the csv should be written. It must be opened in binary mode
* `data`: A list of objects or dicts that should be exported
* `column_definitions`: A list of `ColumnDefinition` objects that define the columns of the csv file and how to get the data for each row
* `timezone`: The timezone into which datetime objects should be converted. Default is timezone set in settings

It raises exceptions if wrong datatypes are passed or if timezone is not known or on unexpected errros.

```python
from datetime import datetime
from openmodule.utils.csv_export import render, ColumnDefinition, CsvFormatType
from openmodule.config import settings

class SomeObject:
    def __init__(self, session_id, entry_time, exit_time, price):
        self.session_id = session_id
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.price = price

# export object
objs = [SomeObject("123", datetime.utcnow(), datetime.utcnow(), 123),
        SomeObject("124", datetime.utcnow(), datetime.utcnow(), 123)]
with open("output.csv", 'wb') as f:
    render(f, objs, [ColumnDefinition("garage", "", CsvFormatType.static_text, settings.RESOURCE),
                     ColumnDefinition("session id", "session_id", CsvFormatType.string),
                     ColumnDefinition("exit time", "exit_time", CsvFormatType.datetime, datetime.max),
                     ColumnDefinition("total price", "price", CsvFormatType.currency_amount)])

# export dict
data = [{"session id": objs[0].session_id, "duration": objs[0].exit_time - objs[0].entry_time}]
with open("output2.csv", 'wb') as f:
  render(f, data, [ColumnDefinition("garage", "", CsvFormatType.static_text, settings.RESOURCE),
                   ColumnDefinition("session id", "session id", CsvFormatType.string),
                   ColumnDefinition("duration", "duration", CsvFormatType.duration)])
```

### Export scheduling

For daily exports which are uploaded using the databox, please use the `schedule_export` function from 
`utils/csv_export.py`. This function randomizes the upload time based on the resource name so uploads are
spread out to not overload the server.

## ColumnDefinition

The `ColumnDefinition` class is used to define the columns of the csv file. It takes the following arguments in constuctor:
* `name`: The name of the column. This is used as header in the csv file
* `field_name`: Attribute name or key in dict of the data object that should be used for this column
* `format_type`: The type of the data in this column. See `CsvFormatType` for possible values
* `default_value`: The default value for this column if the data object does not contain the attribute or key or if value is None. It must be of a type matching format_type. Default is None

## CsvFormatType
* `static_text`: Fills a static text into the column in every row. `default_value` must be a string or enum. `field_name` is ignored
* `string`: Formats data as string. Values must be either string or string enum. Checks
  * does not contain forbidden characters `["\x0d", "\x09"]`
  * string does not start with "@" or "="
  * string does not start with "+" if it is not a valid phone number
  * string does not start with "-" if it is not a valid negative number
* `number`: Formats data as number ("," is comma). Allowed datatypes are int, float, bool, Decimal
* `percentag`: Formats data as percentage ("," is comma and adds "%"). Does not multiply by 100, so 13.3 -> "13,3%". Allowed datatypes are int, float, Decimal
* `datetime`: Converts data into given timezone and formats data as datetime. Allowed datatypes are datetime and string
* `duration`: Formats data in format "H:MM:SS". Allowed datatypes are timedelta, int and float
* `currency_amount`: Formats Cent amounts into € with 2 decimal places (or equivalent for other currencies). Does NOT add currency symbol. Allowed datatype is int

# How to implement an export

We have a util function in the openmodule for getting an iterator for start and end. The function is named `export_iterator()`.
All exports should use this function for iterating over days.

Here is an example how you generate an export.

```python
@dataclasses.dataclass
class LastExportData:
    """Class that holds the data for the export_iterator function."""
    utc_last_export_start: Optional[datetime.datetime] = None
    utc_min_event_time: Optional[datetime.datetime] = None

class Tasks:
    def __init__(self, core: OpenModuleCore, *, db: Optional[Database] = None,
                 settings_provider: Optional[SettingsProvider] = None):
        self.log = logging.getLogger(self.__class__.__name__)
        self.core = core
        self.db = db or core.database
        self.settings_provider = settings_provider or SettingsProvider()

    def create_export_for_day(self, filename, utc_start, utc_end):
      raise NotImplemented("Implement me!")

    def get_utc_start_for_export(self) -> LastExportData:
        """Returns the last export date, the date of the first validation or None if no data is available in the database."""
        with self.db as db:
            last = db.query(LastExport).all()  # this entry is in UTC
            if last:
                return LastExportData(utc_last_export_start=last[0].date, utc_min_event_time=None)
            else:
                # get datetime of first validation in our database
                first_validation = db.query(ValidatedValidation).order_by(ValidatedValidation.created_at).limit(
                    1).first()
                if first_validation:
                    # found a validation, render all days until now
                    return LastExportData(utc_last_export_start=None, utc_min_event_time=first_validation.created_at)
        return LastExportData()

    def create_export(self):
        timezone = gettz(settings.TIMEZONE)
        # creating export is not essential
        try:
            last_export: LastExportData = self.get_utc_start_for_export()
            it: ExportIterator
            for it in export_iterator(timezone, last_export.utc_last_export_start, last_export.utc_min_event_time):
                self.create_export_for_day(it.csv_date_string, it.utc_start, it.utc_end)
                with self.db as db:
                    # truncate table
                    db.query(LastExport).delete()
                    # we save the start as last export date, because the function export_iterator() always adds one day to the last export date
                    db.add(LastExport(date=it.utc_start))
        except Exception as e:
            self.log.exception("Exception during daily validation export")
```

In the above snippet, you can see that we use the function `get_utc_start_for_export()`, that this function either
returns our last export date, the first created validation in our database or the default value for class `LastExportData`.
If the default values are given to the `export_iterator()` function, then the function will decide the start date.

We decided that we will always run the `create_export()` on startup of the application. Therefore, you should add call the function in `app.py`.

```python
def main():
    core = init_openmodule(settings, database=True)
    rpc = RPCServer(context=core.context)

    assert settings.COMPUTE_ID == 1, "This service can only run on the master NUC"

    tasks = Tasks(core)
    # we create an export on startup, because you can check the export and the cronjob overwrites it anyway
    tasks.create_export()
```

## Uploading a file

For uploading files into the Cloud the Databox service is used.
You can find the documentation of the databox service [here](utils.md?#databox-upload)
