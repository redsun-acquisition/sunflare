# Orchestrator

## Initialization

Orchestrator controllers deploy an instance of the {py:class}`~sunflare.engine._wrapper.RunEngine` in order to execute plans. The executable plans are allocated directly in the controller.

```{code-block} python
:caption: my_plugin/config.py

from attrs import define
from sunflare.config import ControllerInfo

@define
class PluginControllerInfo(ControllerInfo):
    param1: int
    param2: int
```

```{code-block} python
:caption: my_plugin/controller.py
import bluesky.plan_stubs as bps

from typing import Mapping
from concurrent.futures import Future

from my_plugin.config import PluginControllerInfo

from sunflare.engine import RunEngine
from sunflare.model import ModelProtocol
from sunflare.virtual import VirtualBus, Signal

from bluesky.protocols import MsgGenerator

class PluginController:

    # a signal emitting
    # a tuple of UID strings
    # when a plan is finished
    sigNewResult = Signal(tuple[str])

    def __init__(
            self,
            ctrl_info: PluginControllerInfo,
            models: Mapping[str, ModelProtocol],
            virtual_bus: VirtualBus
        ) -> None:
        self._ctrl_info = ctrl_info
        self._virtual_bus = virtual_bus
        self._engine = RunEngine()

        self._future: Future[tuple[str]]

        # we want to allocate motors in our
        # controller, but how do we filter
        # the ones we need from the input dict?
        self._motors: dict[str, Any] = {}

        self._positions: list[float] = []

    def move_and_locate(self, motor: str, positions: Sequence[float]) -> MsgGenerator:
        """Move a motor to an absolute position, then read the position back"""
        for pos in positions:
            yield from bps.mv(self._motors[motor], pos)
            current_location = yield from bps.locate(self._motors[motor])
```

Each controller is unique in the experiment it is expected to orchestrate, and the devices involved in such experiments. Redsun relies on [PEP 544](https://peps.python.org/pep-0544/) (a.k.a. structural subtyping) to filter out the models we want to control. There are two ways to achieve this:

- by using the built-in `hasattr` function to determine if a `Model` has the required methods to execute an operation;
- by defining a local `Protocol` with the expected methods and using `isinstance` to check if our `ModelProtocol` respects our custom interface.

In our example, to use the [stub plans] `bps.mv` and `bps.locate`, an interface requires, respectively:

- to implement the [`Movable`] protocol;
- to implement the [`Locatable`] protocol.

To check for the existence of these protocols, we can use two approaches:

- check with `hasattr` if there are models with both method attributes;
- use a local `Protocol` class defining the required signatures.

::::{tab-set}
:::{tab-item} using `hasattr`
```{code-block} python
:caption: my_plugin/controller.py

# continuing __init__() ...
self._my_models = {}
for name, model in models.items():
    if all([hasattr(model, method) for method in ["set", "locate"]])
        self._my_models[name] = model
```

You can also use `dict` comprehension:

```{code-block} python
self._my_models = {
    name: model
    for name, model in models.items if all([hasattr(model, method) for method in ["set", "locate"]])
}
```
:::
:::{tab-item} using a custom `Protocol`
```{code-block} python
:caption: my_plugin/controller.py

# before defining your "PluginController"
from typing import Protocol
from sunflare.engine import Status

from bluesky.protocols import Location

class MotorProtocol:
    def set(self, value) -> Status:
        ...

    def locate(self) -> Location[float]:
        ...

# continuing __init__() ...
self._my_models: dict[str, MotorProtocol] = {}
for name, model in models.items():
    if isinstance(model, MotorProtocol):
        self._my_models[name] = model
```

You can also use `dict` comprehension:

```{code-block} python
self._my_models: dict[str, MotorProtocol] = {
    name: model
    for name, model in models.items if isinstance(model, MotorProtocol)
}
```
:::
::::

Key differences in both approaches:

- using `hasattr` is more performant than `isinstance`, as reported in the [`mypy`] documentation;
  - in our use case though, performance will only marginally impact startup time, and it may be considered negligeble;
- using `isinstance` provides type hints for the models you're storing, while `hasattr` does not; in the example above, your IDE will not provide information on whether `set`/`locate` are methods or object attributes, while `isinstance` will allow your IDE to provide more complete information about them.

The reccomended approach is to use `Protocols` in order to have better type hinting of your code. You should use this approach **only** to allocate the models you need at Redsun initialization, as that will only impact performance when starting the application (and only by a minimal amount) and not impact run-time performance.

### Registration and connection

During initialization we provide the means to execute an experiment (a plan, a group of devices, and a `RunEngine` to perform the plan), but we still don't have ways to control this behavior from the rest of the application.

During startup time, Redsun will call two methods of `ControllerProtocol`:

- {py:attr}`~sunflare.controller.ControllerProtocol.registration_phase`;
- {py:attr}`~sunflare.controller.ControllerProtocol.connection_phase`.

The first will *always* be called before the second. These two methods allow your controller to expose any {py:class}`~sunflare.virtual.Signal` object to the rest of the application, as well as connect
to `Signal` objects provided by other controllers.


```{code-block} python
:caption: my_plugin/controller.py

def set_position_list(self, positions: list[float]) -> None:
    self._positions = positions

def execute_plan(self, motor: str) -> None:
    # the engine will execute the plan in the background,
    # returning a concurrent.futures.Future object
    # which we can use to emit a signal when the plan
    # is finished
    def emit_when_done(fut: Future) -> None:
        self.sigNewResult.emit(fut.result())
    
    self._future = self._engine(self.move_and_locate(motor, self._positions))
    self._future.add_done_callback(emit_when_done)

def registration_phase(self) -> None:
    # first we register the signal in our
    # virtual bus; in this case
    # sigNewResult ...
    self._virtual_bus.register_signals(self)

def connection_phase(self) -> None:
    # ... then we connect relevant signals
    # from an hypothetical ExternalController
    # to local callbacks of our controller;
    self._virtual_bus["ExternalController"]["sigStartPlan"].connect(self.execute_plan)
    self._virtual_bus["ExternalController"]["sigUpdatePositions"].connect(self.set_position_list)
```

You can also connect signals incoming from widgets registered to the virtual bus.

[stub plans]: https://blueskyproject.io/bluesky/v1.13.0a4/plans.html#stub-plans
[`Movable`]: https://blueskyproject.io/bluesky/v1.13.0a4/hardware.html#bluesky.protocols.Movable
[`Locatable`]: https://blueskyproject.io/bluesky/v1.13.0a4/hardware.html#bluesky.protocols.Locatable
[`mypy`]: https://mypy.readthedocs.io/en/stable/protocols.html#using-isinstance-with-protocols
