# Settings

[TOC]

**ℹ Information:** The settings module is often called config module.

The Openmodule settings feature is used to convert environment variables to constant setting values.

The openmodule package uses a global lazy configuration `openmodule.config.settings`. This setting includes some
standard parameters defined in `openmodule.config.GlobalSettings` and parameters from a customizable module. To specify
the module you can call `settings.configure(module)` or you can set the environment variable `SETTINGS_MODULE`. Per
default settings looks for the `config` module (it also looks for the `tests/config` module first for test cases).

## Settings Function

The framework also provides multiple functions for more complex behaviours:

* `debug()`: Returns true if working in a debug environment, i.e. `DEBUG=True` or not in docker and unknown version
* `testing()`: Returns true if the `TESTING` env variable is set
* `database_folder()`: Returns the default database folder, depending on testing() and debug()
* `version()`: Returns the version of the package
* `resource()`: Returns the auth resource
* `dev_device()`: Returns if the device is authenticated at the dev device server or not, useful for connecting to the
  correct dev/prod server
* `config_yaml_path()`: Returns either the env varibale `CONFIG_YAML`or the default value depending on the environment (
  testing, debug, prod)
* `yaml(model, path=None)`: Returns the parsed yaml config based on the model and the path (default config_yaml_path())
* `dist_folder()`: Returns either the env variable `DIST_FOLDER` or the default value depending on the environment

## Global Settings

The framework provides a list of common settings that all device services are using.
They already have a default value and are usable without any configuration.

```python
class GlobalSettings:
    # usual
    NAME = string("NAME", "om_dev_unnamed_1")
    VERSION = version()
    RESOURCE = resource()
    DEBUG = debug()
    TESTING = testing()
    LOG_LEVEL = log_level()
    DATABASE_FOLDER = database_folder()

    # broker env vars
    BROKER_SUB = broker_sub()
    BROKER_PUB = broker_pub()

    LOCAL_DEVELOPMENT = bool("LOCAL_DEVELOPMENT", False)
    is_bridged_slave = is_bridged_slave()
    DIST_FOLDER = dist_folder()
    DEV_DEVICE = dev_device()

    # redis
    REDIS_HOST = string("REDIS_HOST", "localhost")
    REDIS_PASSWORD = string("REDIS_PASSWORD", "") or None
    REDIS_PORT = int("REDIS_PORT", 6379)
    REDIS_DB = int("REDIS_DB", 0)
```
