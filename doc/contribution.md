### Guide for adding the support of a router

#### Creating an extractor class
You need to create a class in <span style="color: green">[*<span style="color: black">inora/lib/Gateway/lib/routers*](../Gateway/lib/routers/)</span>. This class must inherit from `AbstractDevicesExtractor`. This implies having a method called `get_devices_dict` that returns a dictionary with entries like "*&lt;mac-address&gt;:&lt;hostname&gt;*", such as :
```
{
 "D0-87-E2-07-38-BB": "Device1",
 "00-14-22-01-23-45": "Device2",
 "00-1B-63-84-45-E6": "Device3"
}
```

The AbstractDevicesExtractor class gives access to the router IP, its credentials and the poll period between each set of connected hosts retrieval. They can be accessed respectively with :</br>
`super(<yourNewClassName>, self).get_router_ip()`</br> 
`super(<yourNewClassName>, self).get_poll_period()`</br>
`super(<yourNewClassName>, self).get_credentials()["router_login"]` and `super(<yourNewClassName>, self).get_credentials()["router_password"]`

#### Adding the router to the extractor factory

In the `device_extractor_factory` function of [*<span style="color: black">inora/Gateway/inora_gateway.py*](../Gateway/inora_gateway.py)</span>, add an *if* condition with the newly created router :
```
if type == "<MyNewRouter>":
    return MyNewRouterClass(router_ip, poll_period)
```
Where `MyNewRouter` will be the value for the the `router_type` variable in *inora.conf*.

Also, the newly created class must be imported in this file. Example :
```
from lib.routers.bboxconnecteddevicesextractor import BboxConnectedDevicesExtractor
```
