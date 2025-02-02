# Model

The `Model` represents an interface with a device.

The definition of a model is quite fluid, as there are many ways that it can interact with the hardware depending on your needs.

Sunflare provides a protocol, the {py:class}`~sunflare.model.protocols.ModelProtocol`, with a minimal required interface to be recognized by a Redsun application.

Additional parameters can be passed to `ModelProtocol` via the {py:class}`~sunflare.config.ModelInfo` configuration class, by subclassing the latter to provide additional configuration informations.

## In-process models

**in-process** models provide interaction with the device API in the same process:
  - by importing the API as a Python package and use it as a local object;
  - by inheriting from an existing class that encapsulates the commands of your device.

### API as python package

In this usage, a standard model is simply a wrapper around the actual device interface you want to control.

```mermaid
:config: {"theme": "base"}
:align: center
%%{init: { 'theme': 'base', 'themeVariables': { 'primaryColor': '#fefefe', 'lineColor': '#fefefe', } } }%%

    classDiagram
        class DeviceModel {
            -DeviceHandler _handler
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

        DeviceModel *-- DeviceHandler
        ModelInfo <|-- DeviceInfo : inherits from
        DeviceModel o-- DeviceInfo : is aggregated in
```

```{tip}
"Aggregation" means when an object is passed to the constructor of the class.
```

The diagram above is equivalent to:

```python

from device_package import DeviceHandler
from bluesky.protocols import Reading
from event_model import DataKey

class DeviceModel:
    def __init__(self, name: str, model_info: DeviceInfo) -> None:
        self._name = name
        self._model_info = model_info
        self._handler = DeviceHandler()
    
    def configure(self) -> None:
        # here goes your implementation;
        # this is just an example; effectively
        # _handler can have different methods
        # as long as the overall behavior
        # is to configure a parameter
        # of the device
        self._handler.configure()

    def read_configuration(self) -> dict[str, Reading]:
        # here goes your implementation;
        # this is just an example; effectively
        # _handler can have different methods
        # as long as the overall return value
        # is the one of the signature
        return self._handler.read_configuration()
    
    def describe_configuration(self) -> dict[str, DataKey]:
        # here goes your implementation;
        # this is just an example; effectively
        # _handler can have different methods
        # as long as the overall return value
        # is the one of the signature
        return self._handler.describe_configuration()

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
