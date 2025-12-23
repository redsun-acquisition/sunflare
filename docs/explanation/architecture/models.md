# Models

The `Model` represents an interface with a device.

The definition of a model is quite fluid, as there are many ways that it can interact with the hardware depending on your needs.

Models can be developed with two approaches:

- by implementing the [`PModel`][sunflare.model.PModel] with all the required methods and properties;
- inheriting from [`Model`][sunflare.model.Model], which implements the above protocol with pre-configured implementation.

Additional parameters can be passed to the `PModel` via the [`ModelInfo`][sunflare.config.ModelInfo] configuration class, by subclassing the latter to provide additional configuration informations.

## See Also

- [In-Process Model](in-process-model.md) - Detailed guide on implementing models
