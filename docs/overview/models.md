# Models

The `Model` represents an interface with a device.

The definition of a model is quite fluid, as there are many ways that it can interact with the hardware depending on your needs.

Sunflare provides a {py:class}`~sunflare.model.ModelProtocol` with a minimal required interface to be recognized by a Redsun application.

Additional parameters can be passed to the `ModelProtocol` via the {py:class}`~sunflare.config.ModelInfo` configuration class, by subclassing the latter to provide additional configuration informations.

```{toctree}
:maxdepth: 1

in_process_model
```
