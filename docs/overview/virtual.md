# Virtual bus

The {py:class}`~sunflare.virtual.VirtualBus` is a class encapsulating different communication mechanism to allow different controllers and widget to exchange controls and/or data streams. It provides the following features:

- a "Qt-like" mechanism of signal connection through the [`psygnal`] package, where objects can dinamically register signals and connect to remote slots for communication in the main thread;
- a ZMQ publisher/subscriber device which provides a common data exchange channel for multiple endpoints via the [`pyzmq`] package;
  - data can be encoded/decoded via [`msgspec`];
- a {py:obj}`~sunflare.virtual.slot` decorator which can mark your class method as a function connected to a signal;

```{tip}
{py:obj}`~sunflare.virtual.slot` is pure syntactic sugar; it does not provide any advantage at runtime, but renders your code more easy to read for other developers. `psygnal.Signal` can be connected to any function or class method.
```

## Signal connection

The `VirtualBus` allows to create a connection between objects living in different plugins.

Suppose you have the following example:

```{code-block} python
:caption: emitter_plugin.py

class Emitter:
    sigSender = Signal(int)
```

```{code-block} python
:caption: receiver_plugin.py

class Receiver:
    
    def receiver_slot(param: int) -> None:
        print("I received", param)
```

In a normal scenario where you have access to the codebase of both `Emitter` and `Receiver`, you would simply do the following:

```{code-block} python

emitter = Emitter()
receiver = Receiver()

emitter.sigSender.connect(receiver.receiver_slot)
emitter.sigSender.emit(10)

# prints "I received 10"
```

Redsun operates by dinamically loading plugins, which means that `Emitter` and `Receiver` may come from different packages.

The `VirtualBus` takes care of giving a common exposure and retrieval point between different plugins. The catch is that to be able to share a connection, `Emitter` and `Receiver` must be adapted to talk to the bus:

```{code-block} python
:caption: emitter_plugin.py

from sunflare.virtual import VirtualBus

class Emitter:
    sigSender = Signal(int)

    def __init__(self, virtual_bus: VirtualBus) -> None:
        self.virtual_bus = virtual_bus

    def registration_phase(self) -> None:
        self.virtual_bus.register_signals(self)
```

```{code-block} python
:caption: receiver_plugin.py

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

This enforces a specific call order: all `Emitter`-like object must call the `registration_phase` method before any `Receiver`-like´object can call the `connection_phase` method, otherwise there will be a mismatch.

```{note}
If a `Receiver`-like object tries to connect to a non-defined signal, your application will not crash, but there will be simply no connection enstablished with your slots.
```

As a user, you only need to provide these two methods to ensure a safe connection. When Redsun is launched, it takes care of calling `registration_phase` and `connection_phase` in the correct order to ensure a safe connection.

````{warning}
If you're using Sunflare in a non-Redsun application, you'll have to:

- create an instance of `VirtualBus`;
- connect any `Emitter` and `Receiver` objects manually;
- call {py:obj}`~sunflare.virtual.VirtualBus.shutdown` before ending your application;
  - the rationale is that the bus deploys a ZMQ context which has to be gracefully terminated; the `shutdown` method takes care of that.

```{code-block} python

from sunflare.virtual import VirtualBus

bus = VirtualBus()

emitter = Emitter(bus)
receiver = Receiver(bus)

# ... run your application
# before ending the application,
# call the following:
bus.shutdown()
```
````

## Socket connection

The `VirtualBus` uses a [`pyzmq`] queue (called a "forwarder") for sharing a serialized byte stream between different endpoints using the publisher/subscriber pattern.

This pattern can be used in different configurations.

- one-to-one: a single publisher forwards data to a single subscriber;
```mermaid
:config: { "theme": "neutral" }
:align: center

graph LR
    q[["zmq.XSUB | -> | zmq.XPUB"]]
    pub["zmq.PUB"] --> q
    q --> sub["zmq.SUB"]
```

- one-to-many: a single publisher forwards data to a multiple subscribers;
```mermaid
:config: { "theme": "neutral" }
:align: center

graph LR
    q[["zmq.XSUB | -> | zmq.XPUB"]]
    pubA["zmq.PUB"] --> q
    q --> subA["zmq.SUB"]
    q --> subB["zmq.SUB"]
    q --> subC["zmq.SUB"]
```

- many-to-many: multiple publishers forward data to a multiple subscribers;
```mermaid
:config: { "theme": "neutral" }
:align: center

graph LR
    pubA["zmq.PUB"] --> q
    pubB["zmq.PUB"] --> q
    pubC["zmq.PUB"] --> q
    q[["zmq.XSUB | -> | zmq.XPUB"]]
    q --> subA["zmq.SUB"]
    q --> subB["zmq.SUB"]
    q --> subC["zmq.SUB"]
```
- many-to-one: multiple publishers forward data to a single subscriber.
```mermaid
:config: { "theme": "neutral" }
:align: center

graph LR
    pubA["zmq.PUB"] --> q
    pubB["zmq.PUB"] --> q
    pubC["zmq.PUB"] --> q
    q[["zmq.XSUB | -> | zmq.XPUB"]]
    q --> subA["zmq.SUB"]
```

This is transparent to the plugins: they're not aware of how many agents are currently connected to the forwarder; whenever a new message is sent from a publisher, any subscriber who is actively listening (either to a broadcasted message or to a specific topic) will be able to receive the information.

The `sunflare.virtual` module provides a series of pre-shipped classes which allow for easy integration with the `zmq` forwarder:

- {py:class}`~sunflare.virtual.Publisher` (message dispatching);
- {py:class}`~sunflare.virtual.Subscriber` (message reception).

### Serialization with `msgspec`

[`msgspec`] is a *fast* serialization library (according to the author, and backed up by some [benchmarks](https://jcristharif.com/msgspec/benchmarks.html)); combined with the performance of [`pyzmq`], transmission from one point to another becomes easy and fast. Sunflare provides two methods:

- {py:obj}`~sunflare.virtual.encode`;
- {py:obj}`~sunflare.virtual.decode`;

using a common, reusable `msgspec` encoder/decoder for data transmission and reception.

[`psygnal`]: https://psygnal.readthedocs.io/en/stable/
[`pyzmq`]: https://pyzmq.readthedocs.io/en/latest/
[`msgspec`]: https://jcristharif.com/msgspec/
