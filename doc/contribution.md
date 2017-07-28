Guide for adding the support of a router :

Need to create a class in `inora/lib/Gateway/lib/devicesextractor.py`. This class must inherit from `AbstractDevicesExtractor`. This implies having a method called `get_devices_dict` that returns a dictionary with entries like "*&lt;mac-address&gt;:&lt;hostname&gt;*", such as :
```
{
 "D0-87-E2-07-38-BB": "Device1",
 "00-14-22-01-23-45": "Device2",
 "00-1B-63-84-45-E6": "Device3"
}
```

The AbstractDevicesExtractor class gives access to the router IP and to the poll period between each set of connected hosts retrieval. They can be accessed respectively with :</br>
`super(<yourNewClassName>, self).get_router_ip()` and `super(<yourNewClassName>, self).get_poll_period()`
