# Presenters

`Presenters` represent the execution logic of your system.

Where `Models` are "workers" (as they instruct your device to perform a certain task), `Presenters` **can be** "orchestrators", in the sense that they define the sequence of actions that workers must perform through Bluesky [plans].

We highlight "**can be**" because `Presenters` are not limited to that:

- they can consume Bluesky [documents] for on-the-fly processing, intermediate storage or redirection to a GUI (i.e. computing the FFT of an image and sending it to the GUI for display);
- they can provide manual control for device task execution and/or configuration;
  - in comparison to plans (which represents an experimental procedure), one may wish to - for example - manually move a motor stage from the GUI, or change the exposure time of a camera; the `Presenter` in this case acts as a middle-man between the GUI and the device, directly calling Bluesky methods and bypassing the `RunEngine`;
- they can act as communication points with external applications to trigger actions via a custom communication protocol (or wait for possible commands incoming by said applications).

`Presenters` are meant to communicate between each other via the {py:class}`~sunflare.virtual.VirtualBus`, which takes care of redirecting information (commands and/or documents) to the appropriate destination (whether it is another `Presenter` or a `View`).

All controllers must implement the {py:class}`~sunflare.presenter.PPresenter` interface to be recognized by Redsun.

The {py:class}`~sunflare.presenter.PPresenter` requires three things in its initialization:

- a reference to a subclass of {py:class}`~sunflare.config.ControllerInfo`, to provide additional parameters;
- a `Mapping[str, PModel]` of the allocated models in the session;
- a reference to the {py:class}`~sunflare.virtual.VirtualBus` in order to provide a communication point with other controllers and widgets.

```{toctree}
:maxdepth: 1

orchestrator_controllers
```

[documents]: https://blueskyproject.io/bluesky/main/documents.html
