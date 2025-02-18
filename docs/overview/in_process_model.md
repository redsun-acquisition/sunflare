# In-process models

**in-process** models provide interaction with the device API in the same process:
  - by importing the API as a Python package and use it as a local object: [API via aggregation](#api-via-aggregation);
  - by inheriting from an existing class that encapsulates the commands of your device: [API via inheritance](#api-via-inheritance).

## API via aggregation

"Aggregation" means when an object is constructed inside a class.

In this usage, a standard model is simply a wrapper around the actual device interface you want to control.

The wrapped interface is often referred to as `handler`, although it varies depending on implementation details.
The external application should not interact directly with the `handler` object; instead, the Model wrapping it should take care of calling the appropriate methods of the `handler` to perform the required tasks.

```{tip}
It is good practice to mark your handler object via a double underscore `__`, i.e. `__handler`, symbolizing that this is a *private* attribute (meaning that only your Model object can use it internally and it is not accessible from the outside). In truth, Python **does not really** enforce private attributes - meaning that there are ways to circumvent the privacy - but it is considered standard practice to annotate them in this manner.
```

::::{tab-set}
:::{tab-item} UML
```mermaid
:config: { "theme": "neutral", "fontFamily": "Courier New" }
:align: center

    classDiagram
        class DeviceModel {
            -DeviceHandler __handler
            +DeviceInfo model_info
            +str name
            +None parent
            configure() None
            read_configuration() dict[str, Reading]
            describe_configuration() dict[str, DataKey]
        }
        class DeviceHandler {
            +int param1
            +float param2
            device_method() void
        }
        class ModelInfo {
        }
        class DeviceInfo {
            +int param1
            +float param2
        }

        DeviceModel *-- DeviceHandler
        ModelInfo <|-- DeviceInfo : inherits from
        DeviceModel o-- DeviceInfo : is aggregated in
```
:::
:::{tab-item} Python
```{code-block} python
:caption: my_plugin/config.py

from attrs import define
from sunflare.config import ModelInfo

@define
class DeviceInfo(ModelInfo):
    param1: int
    param2: float
```

```{code-block} python
:caption: my_plugin/model.py

from my_plugin.config import DeviceInfo
from device_package import DeviceHandler
from bluesky.protocols import Reading
from event_model import DataKey

class DeviceModel:
    def __init__(self, name: str, model_info: DeviceInfo) -> None:
        self._name = name
        self._model_info = model_info

        # unpack the parameters you need
        # to initialize DeviceHandler,
        # or provide them hard-coded
        param1 = model_info.param1
        param2 = model_info.param2
        self.__handler = DeviceHandler(int_param=param1, float_param=param2, bool_param=True)
    
    def configure(self) -> None:
        # here goes your implementation;
        self.__handler.configure()

    def read_configuration(self) -> dict[str, Reading]:
        # here goes your implementation;
        return self.__handler.read_configuration()
    
    def describe_configuration(self) -> dict[str, DataKey]:
        # here goes your implementation;
        return self.__handler.describe_configuration()

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent(self) -> None:
        return None
    
    @property
    def model_info(self) -> DeviceInfo:
       return self._model_info
```
:::
::::

Furthermore, a single Model can encapsulate multiple handlers, each of them with different functionalities. Keep in mind that it is your responsability (as developer) to associate the execution of Bluesky messages with the appropriate device handler.

```{code-block} python
:caption: my_plugin/config.py
from attrs import define
from sunflare.config import ModelInfo
from typing import Any

@define
class MyModelInfo(ModelInfo):
    camera_parameters: dict[str, Any]
    motor_parameters: dict[str, Any]
```

```{code-block} python
:caption: my_plugin/model.py

# a dummy representation of a plugin package that encapsulates
# a Model wrapping controls for a camera and a motor
from device_package import CameraHandler, MotorHandler
from my_plugin.config import MyModelInfo

class MyModel:
    def __init__(self, name: str, model_info: MyModelInfo) -> None:
        self._name = name
        self._model_info = model_info

        self.__motor_handler = MotorHandler(**model_info.motor_parameters)
        self.__camera_handler = CameraHandler(**model_info.camera_parameters)

```

## API via inheritance

Using aggregation to control your device interface may be impractical if `DeviceHandler` already leverages a lot of internal code. Inheriting your Model from a pre-existing class gives the benefit of reusing it without having to rewrite any of the internals.

::::{tab-set}
:::{tab-item} UML
```mermaid
:config: { "theme": "neutral", "fontFamily": "Courier New" }
:align: center

    classDiagram
        class DeviceModel {
            +DeviceInfo model_info
            +str name
            +None parent
            configure() None
            read_configuration() dict[str, Reading]
            describe_configuration() dict[str, DataKey]
        }
        class DeviceHandler {
            device_method() void
        }
        class ModelInfo {
        }
        class DeviceInfo {
            +int param1
            +float param2
        }

        DeviceModel <|-- DeviceHandler
        ModelInfo <|-- DeviceInfo : inherits from
        DeviceModel o-- DeviceInfo : is aggregated in
```
:::
:::{tab-item} Python
```{code-block} python
:caption: my_plugin/config.py

from attrs import define
from sunflare.config import ModelInfo

@define
class DeviceInfo(ModelInfo):
    param1: int
    param2: float
```

```{code-block} python
from my_plugin.config import DeviceInfo
from device_package import DeviceHandler
from bluesky.protocols import Reading
from event_model import DataKey

class DeviceModel(DeviceHandler):
    def __init__(self, name: str, model_info: DeviceInfo) -> None:
        self._name = name
        self._model_info = model_info

        # DeviceInfo can provide
        # any initialization parameters
        # required by DeviceHandler.__init__
        super().__init__(int_param=param1, float_param=param2, bool_param=True)
    
    def configure(self) -> None:
        # here goes your implementation;
        super().configure()

    def read_configuration(self) -> dict[str, Reading]:
        # here goes your implementation;
        return super().read_configuration()
    
    def describe_configuration(self) -> dict[str, DataKey]:
        # here goes your implementation;
        return super().describe_configuration()

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent(self) -> None:
        return None
    
    @property
    def model_info(self) -> DeviceInfo:
       return self._model_info
```
:::
::::

Just like in the aggregated API, your model can also inherit from multiple classes. Again, it is your responsibility (as developer) to ensure that the appropriate Bluesky protocols are invoked on the correct device.

```{code-block} python
:caption: my_plugin/config.py
from attrs import define
from sunflare.config import ModelInfo
from typing import Any

@define
class MyModelInfo(ModelInfo):
    camera_parameters: dict[str, Any]
    motor_parameters: dict[str, Any]
```

```{code-block} python
:caption: my_plugin/model.py

# a dummy representation of a plugin package that encapsulates
# a Model wrapping controls for a camera and a motor
from device_package import CameraHandler, MotorHandler
from my_plugin.config import MyModelInfo

class MyModel(CameraHandler, MotorHandler):
    def __init__(self, name: str, model_info: MyModelInfo) -> None:
        self._name = name
        self._model_info = model_info

        super(MotorHandler, self).__init__(**model_info.motor_parameters)
        super(CameraHandler, self).__init__(**model_info.camera_parameters)
```

## Key differences

Although they may initially look similar, there are key differences and advantages in each approach.

Aggregation is useful...
- ... when you want to have a more fine-grained control over your device;
- ... when your device interface doesn't have an actual class encapsulating methods and parameters but instead uses a different programming paradigm;
- ... when you don't want to expose certain behaviors of your device to the end-user (a.k.a. inhibiting the possibility to call public methods);
- ... when your device interface is built using another language (C++, Rust, ...) and you want to keep a minimal level of abstraction between the model and the handler;
- ... when your handler actually controls the interaction with multiple devices topology and you want to expose only a sub-set of those functionalities.

An example candidate for aggregation is the [`pymmcore-plus`] package, which wraps the controls of multiple Micro-Manager devices behind the [`CMMCorePlus`] interface and provides additional functionalities (such as the [`MDAEngine`]).

Inheritance is useful...
- ... when your device has a lot of code and you want to quickly wrap it to be Bluesky-compatible;
- ... when it provides extra functionalities that allow to work with remote devices by default;
- ... when it is already a Bluesky-compatible device and you just want to make it as a plugin for Redsun.

Example candidates for inheritance are the [`microscope`] and [`openwfs`] packages, as they provide pre-configured interfaces that can be extended with additional Bluesky methods.

[`pymmcore-plus`]: https://pymmcore-plus.github.io/pymmcore-plus/
[`cmmcoreplus`]: https://pymmcore-plus.github.io/pymmcore-plus/api/cmmcoreplus/
[`mdaengine`]: https://pymmcore-plus.github.io/pymmcore-plus/guides/mda_engine/
[`microscope`]: https://python-microscope.org/
[`openwfs`]: https://github.com/IvoVellekoop/openwfs
