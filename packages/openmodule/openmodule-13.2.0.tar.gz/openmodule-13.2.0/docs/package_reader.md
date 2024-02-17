# Package Reader

[TOC]

The package reader allows you to read installed services and their configuration.
For this the device service "Service Misc" has to be running on the system.

The Misc service is needed because it implements the routine which reads the installed services and their configuration.
The Openmodule `PackageReader` only sends RPCs calls to the Misc service.

## Examples

```python
from openmodule.utils.package_reader import PackageReader

package_reader = PackageReader()
# get all packages with a specific hardware type prefix
packages = package_reader.list_by_hardware_type("payment-arivo")
# get all packages with a specific software type prefix
packages = package_reader.list_by_software_type("validation_provider")
# get a specific device service
service = package_reader.get_service_by_name("om_pcard_validation_1")
# get services by parent type
services = package_reader.list_by_parent_type("io-modbus")
```

## Testing

For testing a mock version of the package reader is available. Example:

```python
from openmodule_test.package_reader import MockPackageReader

package_reader = MockPackageReader()
package_reader.services.add_hardware_package("hw_compute_nuc_1", hardware_type=["compute"], ip="10.15.0.200")
package_reader.services.add_software_package("om_fancy_assistant_1", parent="hw_compute_nuc_1",
                                             env={"LOG_LEVEL": " DEBUG"})

print(package_reader.get_service_by_name("om_fancy_assistant_1").parent.name)
# hw_compute_nuc_1
```

## Bridged Slave/Master Detection

Some services should behave differently if they are started on a bridged master device or bridged slave device (i.e.
prevent double rpc-responses, prevent double code execution).
For this each NUC is setup with a COMPUTE_ID.
The master NUC always has `COMPUTE_ID=1`. For easier detection the functions `is_bridged_slave()`
and `is_bridged_master()` are available.

### Config

* The `COMPUTE_ID` env variable is responsible for the slave/master detection. Per default the COMPUTE_ID is set
  to `COMPUTE_ID=1`, therefore a master NUC.
* If you want to switch to a "slave" NUC, you can either set it directly with the env variable or override it for test
  cases (@override_settings(COMPUTE_ID=2))

### Example

The DSGVO container takes care of the anonymization. For this it saves links between vehicle_ids and session_ids and
forwards requests to anonymize session_ids with the appropriate vehicle_ids.
If we have a bridged installation only the master DSGVO container should perform these tasks. The DSGVO container on
slave devices should only anonymize data on its device.

* RPC for anonymization and linking session to vehicle only registered `if is_bridged_slave() is False`
