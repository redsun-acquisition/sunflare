# `sunflare.controller`

Controllers come in two forms:

- ``typing.Protocol`` classes:
  - no inheritance required, allows full customization of the controller;
  - users will have to implement each interface on their own in a controller class;
  - available protocols:
    - {py:class}`~sunflare.controller.PPresenter` (for class initialization)
    - {py:class}`~sunflare.controller.HasShutdown` (for clearing held resources)
    - {py:class}`~sunflare.controller.HasRegistration` (for registering signals)
    - {py:class}`~sunflare.controller.HasConnection` (for connecting signals to local methods)
- boilerplate mixin classes:
  - minimal, reusable components to provide a specific functionality
  - inheritance is required
  - available mixins:
    - {py:class}`~sunflare.controller.Controller` (minimal base controller)
    - {py:class}`~sunflare.controller.Sender` (implements {py:class}`~sunflare.controller.HasRegistration` protocol)
    - {py:class}`~sunflare.controller.Receiver` (implements {py:class}`~sunflare.controller.HasConnection` protocol)
    - {py:class}`~sunflare.controller.SenderReceiver` (union of previous two mixins)

```{eval-rst}
.. automodule:: sunflare.controller
    :members:
    :member-order: bysource
```
