# The Healthz System

[TOC]

## Introduction

The healthz system is responsible for monitoring our services. Services can also indicate if a hardware component is
working properly or is reporting an error. Thus, a developer may consider two variants of checks:

* Software checks: These are checks that are checking about an erroneous state of the software: e.g. database
  inconsistent, something is misconfiguration, etc. These checks are not visible to the customer.
* Hardware checks: These are checks that are checking about a hardware component: e.g. Camera disconnected, the cash
  register is full, etc. These checks are visible to the customer.

A service which is not responding to healthz requests will be considered crashing. If a service has a parent hardware
component, e.g. the alpr service has the camera as its parent, then the alpr service is considered the "driver" of the
hardware component. If te driver of the hardware component is not running (i.e. it is crashing, or non-responsive), then
no checks will be visible or processed for the hardware component.

All checks should be registered as soon as possible (i.e. on startup). Before the check is firing or cleared it is
in the state "no-data" as we cannot decide it's state until the service has set it's state once.

The healthz system also contains a metric system which allows services to report metrics for external monitoring.

## About Hardware Packages and Drivers

Every hardware component requires a so called "driver" which is the main indicator if the device is running.
A service is a driver for a hardware package if has it set as it's `PARENT`.

#### Services which are driver for multiple hardware packages

Due to limitations in the package format, we currently hack this by manually mapping such services to multiple hardware
packages. This is done in the health
poller [in service-misc/health.py](https://gitlab.com/accessio/openmodule/service-misc/-/blob/v2/src/refactor/health.py#L39)
.

## Examples

### Hardware check for my parent package

You would use this setup if you have 1 parent hardware package for which you are soley responsible

```python
core = init_openmodule(settings)
core.health.add_check("connected", "Camera Connection",
                      "This check monitors if the camera is connected and we receive a videostream.",
                      parent=True)  # note parent=True is the equivalent to "package=core.settings.PARENT"

while True:
    try:
        connect()
        core.health.check_success("connected", parent=True)  # after connecting we clear the check
        while is_connected():
            receive_images()
    except NetworkError:
        core.health.check_fail("connected", parent=True)  # we have lost connection -> fire the check!
        close_connection()

```

### Hardware check for a different hardware package

You would use this setup if you have some service which can detect errors at other hardware component, and this
component will always stay the same. E.g. the tracking service fires an check for it's camera.

```python

core = init_openmodule(settings)
tracking_config = load_config()

core.health.add_check("detection-rate", "Detection Rate",
                      "This check monitors if we are detecting license plates when vehicles are passing though.",
                      package=tracking_config.source_camera)

while True:
    do_tracking_stuff()
    if detection_rate < 0.9:
        core.health.check_fail("detection-rate", package=tracking_config.source_camera,
                               message=f"Detection may be as low as {(detection_rate * 100):.2f}%")
    else:
        core.health.check_success("detection-rate", package=tracking_config.source_camera)
```

### Hardware check for a dynamic number of hardware packages

You would use this setup if you have some service which can detect errors at other hardware components. For
example the camoperator could check an error condition for all cameras, but the number of cameras will
change during the runtime of the service.

**Note** in this case you may also want to read
about [services which are driver for multiple hardware packages](#services-which-are-driver-for-multiple-hardware-packages)

```python
core = init_openmodule(settings)
core.health.add_check_template("position-alarm", "Position Alarm",
                               "This check monitors if the camera was moved via the camera's position alarm function.")

while True:
    cameras_i_monitor = get_monitored_cameras()  # ["hw_avigilon_h5bullet_1", "hw_avigilon_h5bullet_2"]
    core.health.update_template_packages("position-alarm", packages=cameras_i_monitor)

    for camera in cameras_i_monitor:
        if camera_was_moved(camera):
            core.health.check_fail("position-alarm", package=camera)
        else:
            core.health.check_success("position-alarm", package=camera)
```

### Software checks for myself

You would use this for example if you have detected a software issue which warrants an check. Note that
in this case the service **must not** crash after setting the check, as it needs to be running in order
for checks to be processed. If it is so bad that you crash, you should rather just send a sentry exception and crash.

```python
core = init_openmodule(settings)
core.health.add_check("update-error", "Update Error",
                      "The updater fires this check if it is unable to install updates.")

try:
    update_software()
    core.health.check_success("update-error")
except Exception as e:
    core.health.check_fail("update-error", message=str(e))
```

## Technical details and quirks

* The `message` of an check is only displayed if the check is firing. While always the last message will be shown to the
  user, no effort is made to check if the message has changed (i.e. notify the user a second time if a different message
  occurs). So you probably only want to have one message.

* Some services are parent for multiple hardware devices, this is hot-fixed in service-misc which holds a list of
  such services and then constructs the health status accordingly. See "Hardware check for multiple parent packages".

* The difference between being the driver or not the driver of a package is that as described above the hardware
  component will be considered completely offline if the driver is not running. So for a high time check that some
  other service does, we do not consider it the "driver".

* checks are polled, so firing an check and crashing won't do much, it will just show your service as crashing.
* The `status` in `pong` is "error" if any check is status "fail" (not if "no_data"). There is also `message` in pong 
  which is set to the message of the first failed check.

## Metrics

The healthz metrics system is built in the assumption that the metrics are collected and converted to a prometheus like
time series.

They support the use of labels.
Description in prometheus docs:
> Use labels to differentiate the characteristics of the thing that is being measured.

Labels are defined at metric creation and should all be set when a value is set.

Additionally, all metric informations should be uniform (`English only, no translations`).

The following types of metrics are supported:

* `str`: A string is a value that can be set to any string. It is used to store things like the current version
  of the software, or the current state of a machine. Can only be set, not incremented or decremented.
* `count`: A counter is a monotonically increasing value. It is used to count things like the number of
  requests, or the number of errors. It is not used to measure the time something took, or the size of something. It
  cannot be decremented.
* `gauge`: A gauge is a value that can go up and down. It is used to measure things like the current memory usage,
  or the number of active users. It is not used to count things. Can be set, incremented and decremented.

Metrics can be cleared using the `metric_clear` method. It optionally takes a list of label dictionaries to keep. 
If the metric will not be used anymore use `remove_metric` instead. 
(`metric_clear` deletes all values in a metric, `remove_metric` deletes the metric completely)
A single metric value can be deleted using the `metric_set` method with value `None`.


### Examples
    
```python
core = init_openmodule(settings)
core.health.add_metric("sessions_started", HealthMetricType.count, "Started sessions", 
                       "Counts the total number of new sessions", labels={"gate", "has_access", "double_entry"})
core.health.add_metric("sessions", HealthMetricType.gauge, "Active sessions", "The total number of active sessions",
                       labels={"gate", "has_access"})
core.health.metric_inc("sessions_started", gate="gate_1", has_access=True, double_entry=True)
core.health.metric_dec("sessions", 5, gate="gate_1", has_access=True, double_entry=True)
core.health.metric_set("sessions", None, gate="gate_1", has_access=True)  # Delete the value
core.health.metric_clear("sessions_started", values_to_keep=[{"gate": "gate_1", "has_access": True, "double_entry": True}])  # Clear all but the given labels
```

### Units of Measurement

In order to properly process and display the collected metric data, it is possible to hint the unit of measurement in the name of
the metric by appending (at the end of the name-string!) the unit enclosed in parenthesis e.g. `CPU Usage (%)`,  `RAM Used (B)`, `Total Cost (money)` etc.
Currently, the following units are supported:
* `B` - Bytes
* `b` - Bits
* `s` - Seconds
* `ts` - UNIX Timestamp
* `money` - Unit for currencies
  * Requires an additional label to distinguish between specific units e.g. EUR, GBP, CHF
  * The amount is provided as an integer and requires conversion from an integer to a float. Example: money=235 with currency="EUR" results in &#x20AC;2,35
* other units, such as: `°C`, `%` etc.
* no units for simple amount measurements e.g. counting sessions or accesses

If required, a unit can also be prefixed:
* Bytes - `kB` (kilo-Bytes), `MB` (Mega-Bytes), `GB` (Giga-Bytes), ...
* Seconds - `ms` (mili-seconds), ...

Units can also be suffixed:
* Bytes - `B/s` (Bytes per seconds e.g. for upload speed measurements)

Examples:

```python
core = init_openmodule(settings)

# money (settings.CURRENCY="EUR")
core.health.add_metric("open_costs", HealthMetricType.count, "Open costs (money)", 
                       "Counts the total amount of open costs", labels=["currency"])
core.health.metric_inc("open_costs", 42, currency=settings.CURRENCY)  # the amount equals to 0.42 Euros

# CPU usage (%)
core.health.add_metric("system_cpu_usage_ratio", HealthMetricType.gauge, "CPU usage (%)", 
                       "CPU usage in percent", labels=["nuc_version", "cpu_model", "cpu_cores"], package=compute_package)
core.health.set_metric("system_cpu_usage_ratio", get_cpu_percent(), package=compute_package, **cpu_labels)

# Docker boot time (ts)
core.health.add_metric("docker_boot_time", HealthMetricType.gauge, "Boot time of Docker Container (ts)", 
                       "Last boot time in seconds since epoch time", labels=["version"], package=some_package)
core.health.set_metric("docker_boot_time", get_docker_boot_time(), package=some_package, **some_labels)

# Finished Sessions (no unit)
core.health.add_metric("finished_sessions", HealthMetricType.count, "Finished Sessions",
                       "Counts the total amount of finished sessions")
core.health.metric_inc("finished_sessions", 1)

# Terminal serial number (no unit; for checks, where terminal number is fetched periodically)
core.health.add_metric("terminal_number", HealthMetricType.str, "Terminal Number",
                       "Metric for current serial number of the connected terminal")
core.health.metric_set("terminal_number", get_serial_number())
```

### Reserved labels

The following labels are reserved by the server & Prometheus and must not be used: 
* `instance`, `job`, `metric_name`, `package_id`, `package_name`, `resource`, `source`, `compute_id`, `environment`
* Anything beginning with `__` or `grafana_`

### Thread safety

Metrics are not thread safe! However, as long as you manipulate a specific metric (same id) only in one thread you 
should be fine.


### Daemon services

A daemon service might require that only the service on the main nuc exports specific metrics. This is done by
checking `is_bridged_master()` before manipulating the metric.

```python
from openmodule.config import is_bridged_master
if is_bridged_master():
    core.health.metric_inc("sessions_started", gate="gate_1", has_access=True, double_entry=True)
```
