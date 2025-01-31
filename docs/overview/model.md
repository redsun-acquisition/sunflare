# Model

The `Model` represents an interface with a device.

The definition of a model is quite fluid, as there are many ways that it can interact with the hardware depending on your needs.

## In-process models

We make a distinction between **in-process** models and **remote** models.

- **in-process** models are models that provide interaction with the device API in the same process:
  - by importing the API as a Python package and use it as a local object;
  - by inheriting from an existing class that encapsulates the commands of your device.

### API as python package

In this usage, a standard model is simply a wrapper around the actual device interface you want to control.

```{figure} ../images/dark/model_device_wrapper.png
:name: model-wrap
:width: 50%
:class: img-theme-switch

A model wrapping a device interface.
```
