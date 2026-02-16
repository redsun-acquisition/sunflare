# Virtual bus

The [`VirtualBus`][sunflare.virtual.VirtualBus] is a class encapsulating different communication mechanism to allow different presenters and widgets to exchange controls and/or data streams. It provides a "Qt-like" mechanism of signal connection through the [`psygnal`](https://psygnal.readthedocs.io/en/stable/) package, where objects can dinamically register signals and connect to remote slots for communication in the main thread.

## Signal connection

The `VirtualBus` allows to create a connection between objects living in different plugins.

Suppose you have the following example:

```python title="emitter_plugin.py"
class Emitter:
    sigSender = Signal(int)
```

```python title="receiver_plugin.py"
class Receiver:

    def receiver_slot(param: int) -> None:
        print("I received", param)
```

In a normal scenario where you have access to the codebase of both `Emitter` and `Receiver`, you would simply do the following:

```python
emitter = Emitter()
receiver = Receiver()

emitter.sigSender.connect(receiver.receiver_slot)
emitter.sigSender.emit(10)

# prints "I received 10"
```

Redsun operates by dinamically loading plugins, which means that `Emitter` and `Receiver` may come from different packages.

The `VirtualBus` takes care of giving a common exposure and retrieval point between different plugins. The catch is that to be able to share a connection, `Emitter` and `Receiver` must be adapted to talk to the bus:

```python title="emitter_plugin.py"
from sunflare.virtual import VirtualBus

class Emitter:
    sigSender = Signal(int)

    def __init__(self, virtual_bus: VirtualBus) -> None:
        self.virtual_bus = virtual_bus

    def registration_phase(self) -> None:
        self.virtual_bus.register_signals(self)
```

```python title="receiver_plugin.py"
from sunflare.virtual import VirtualBus

class Receiver:

    def __init__(self, virtual_bus: VirtualBus):
        self.virtual_bus = virtual_bus

    def receiver_slot(param: int) -> None:
        print("I received", param)

    def connection_phase(self) -> None:
        self.virtual_bus["Emitter"]["sigSender"].connect(self.receiver_slot)
```

With this modifications, `Emitter` has informed the `VirtualBus` of the existence of `sigSender`, and `Receiver` can retrieve `sigSender` from `Emitter` to connect the signal to its slot `receiver_slot`.

This enforces a specific call order: all `Emitter`-like object must call the `registration_phase` method before any `Receiver`-like object can call the `connection_phase` method, otherwise there will be a mismatch.

!!! note
    If a `Receiver`-like object tries to connect to a non-defined signal, your application will not crash, but there will be simply no connection enstablished with your slots.

As a user, you only need to provide these two methods to ensure a safe connection. When Redsun is launched, it takes care of calling `registration_phase` and `connection_phase` in the correct order to ensure a safe connection.

!!! warning "Using Sunflare without Redsun"
    If you're using Sunflare in a non-Redsun application, you'll have to:

    - create an instance of `VirtualBus`;
    - ensure `Emitter` objects call their `registration_phase` method before `Receiver` objects call their `connection_phase` method.

    ```python
    from sunflare.virtual import VirtualBus

    bus = VirtualBus()

    emitter = Emitter(bus)
    receiver = Receiver(bus)

    # Register signals first
    emitter.registration_phase()

    # Then connect to them
    receiver.connection_phase()

    # ... run your application
    ```
