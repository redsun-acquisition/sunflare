# `sunflare.presenter`

Presenters come in two forms:

- ``typing.Protocol`` classes:
  - no inheritance required, allows full customization of the controller;
  - users will have to implement each interface on their own in a controller class;
  - available protocols:
    - {py:class}`~sunflare.presenter.PPresenter` (for class initialization)
    - {py:class}`~sunflare.presenter.HasShutdown` (for clearing held resources)
    - {py:class}`~sunflare.presenter.HasRegistration` (for registering signals)
    - {py:class}`~sunflare.presenter.HasConnection` (for connecting signals to local methods)
- boilerplate mixin classes:
  - minimal, reusable components to provide a specific functionality
  - inheritance is required
  - available mixins:
    - {py:class}`~sunflare.presenter.Presenter` (minimal base controller)
    - {py:class}`~sunflare.presenter.Sender` (implements {py:class}`~sunflare.presenter.HasRegistration` protocol)
    - {py:class}`~sunflare.presenter.Receiver` (implements {py:class}`~sunflare.presenter.HasConnection` protocol)
    - {py:class}`~sunflare.presenter.SenderReceiver` (union of previous two mixins)

```{eval-rst}
.. automodule:: sunflare.presenter
    :members:
    :member-order: bysource
```
