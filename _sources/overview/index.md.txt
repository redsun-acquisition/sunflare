# Overview

This section illustrates the contents of the package, how to use the provided components for each layer and how these components fit in the Bluesky ecosystem.

## Models

The `Model` represents an interface with a device.

The definition of a model is quite fluid, as there are many ways that it can interact with the hardware depending on your needs.

Sunflare provides a {py:class}`~sunflare.model.protocols.ModelProtocol` with a minimal required interface to be recognized by a Redsun application.

Additional parameters can be passed to the `ModelProtocol` via the {py:class}`~sunflare.config.ModelInfo` configuration class, by subclassing the latter to provide additional configuration informations.

```{toctree}
:maxdepth: 2

in_process_model
```

## Controllers

`Controllers` represent the execution logic of your system.

Where `Models` are "workers" (as they instruct your device to perform a certain task), `Controllers` **can be** "orchestrators", in the sense that they define the sequence of actions that workers must perform through Bluesky [plans].

We highlight "**can be**" because `Controllers` are not limited to that:

- they can consume Bluesky [documents] for on-the-fly processing, intermediate storage or redirection to a GUI (i.e. computing the FFT of an image and sending it to the GUI for display);
- they can provide manual control for device task execution and/or configuration;
  - in comparison to plans (which represents an experimental procedure), one may wish to - for example - manually move a motor stage from the GUI, or change the exposure time of a camera; the `Controller` in this case acts as a middle-man between the GUI and the device, directly calling Bluesky methods and bypassing the `RunEngine`;
- they can act as communication points with external applications to trigger actions via a custom communication protocol (or wait for possible commands incoming by said applications).

`Controllers` are meant to communicate between each other via the {py:class}`~sunflare.virtual.VirtualBus`, which takes care of redirecting information (commands and/or documents) to the appropriate destination (whether it is another `Controller` or a `Widget`).

All controllers must implement the {py:class}`~sunflare.controller.ControllerProtocol` interface to be recognized by Redsun.

```{toctree}
:maxdepth: 2

controllers
```

[plans]: https://blueskyproject.io/bluesky/main/plans.html
[documents]: https://blueskyproject.io/bluesky/main/documents.html
