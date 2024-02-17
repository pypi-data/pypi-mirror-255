# SettingsProvider

[TOC]

SettingsProvider offers easy use of getting settings via the settings RPC. 
The SettingsProvider is thread-safe and implements caching of recently used settings 
together with invalidation triggered by message.

## Behavior

### Return values and Exceptions

Exceptions are thrown if a failure happens (timeout, conversion to target type failed, ...). 
If a settings is not found, None is returned. There exists functions with "_no_exception" postfix 
where exceptions are caught and logged and a fallback value is returned in this case.

### Caching

The values from cache are used if
 * a cached value is found for \<key\>/\<scope\>
 * the value is not expired (default is less than 300 seconds old)
 * the value can be parsed to the requested data type

Otherwise the value is requested with the RPC. All successfully retrieved values are put in the cache. 
In get_many all values are reloaded if one key is not found in cache.

## Usage

```python
from openmodule.utils.settings import SettingsProvider
settings = SettingsProvider()

# In case the setting is of a known type (defined in the settings_models) specifying the type is optional and only 
# useful if your type differs from the one in the settings_models (e.g. less fields, different field parsing)
result = settings.get("common/garage_settings")
result = settings.get("common/garage_settings", custom_type=MyGarageSettingsType)

# For settings of unknown type (Though those should not exist since the settings_models should be complete) you *NEED*
# to specify the type
result = settings.get("key1", custom_type=ResultType)

# A scope can be specified for the settings.
result = settings.get("key1", "scope", custom_type=ResultType)

# The defined settings are Type Hinted such that the IDE types the return value correctly and tells you if the
# setting expects a scope or not. Unknown types are typed such that the return value matches the custom_type
# The following lines should be highlighted as 'Unexpected type(s)' by the IDE
result = settings.get("common/garage_settings", "scope")
result = settings.get("gate_control/mode")
result = settings.get("key1", "scope")
result = settings.get("key1")
# The following line should *NOT* be highlighted as 'Unexpected type(s)' by the IDE
result = settings.get("common/garage_settings")
result = settings.get("common/garage_settings", custom_type=ResultType)
result = settings.get("common/garage_settings", "scope", custom_type=ResultType)
result = settings.get("gate_control/mode", "scope")
result = settings.get("gate_control/mode", "scope", custom_type=ResultType)
result = settings.get("gate_control/mode", custom_type=ResultType)
result = settings.get("key1", "scope", custom_type=ResultType)
result = settings.get("key1", custom_type=ResultType)
# Unfortunately custom_type=None is not highlighted as 'Unexpected type(s)' by the IDE because TypeVar for 'Not None'
# is not supported by PyCharm. This is a known issue: https://github.com/python/mypy/issues/8881
# passing custom_type None results in using the type from the settings_models, if the setting is not known this will
# result in a KeyError
result = settings.get("common/garage_settings", custom_type=None)
result = settings.get("key1", custom_type=None)
result = settings.get("key1", "scope", custom_type=None)

# in get_many you can specify your return type for every setting you want to get in scope.
# Known settings can be specified with None to use the type from the settings_models
relevant_settings = settings.get_many({"common/garage_settings": None, "key1": ResultType})

# A scope can be specified for *all* settings in get_many.
relevant_settings = settings.get_many({"common/garage_settings": None, "key1": ResultType}, "scope")

# get_many is not Type Hinted.
```
