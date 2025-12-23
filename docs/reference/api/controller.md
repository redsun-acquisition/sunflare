# sunflare.presenter

Presenters come in two forms:

## Protocols

`typing.Protocol` classes - no inheritance required, allows full customization of the controller:

- Users will have to implement each interface on their own in a controller class
- Available protocols:
  - [`PPresenter`][sunflare.presenter.PPresenter] (for class initialization)
  - [`HasShutdown`][sunflare.virtual.HasShutdown] (for clearing held resources)
  - [`HasRegistration`][sunflare.virtual.HasRegistration] (for registering signals)
  - [`HasConnection`][sunflare.virtual.HasConnection] (for connecting signals to local methods)

## Mixin Classes

Boilerplate mixin classes - minimal, reusable components to provide a specific functionality:

- Inheritance is required
- Available mixins:
  - [`Presenter`][sunflare.presenter.Presenter] (minimal base controller)
  - [`Sender`][sunflare.presenter.Sender] (implements [`HasRegistration`][sunflare.virtual.HasRegistration] protocol)
  - [`Receiver`][sunflare.presenter.Receiver] (implements [`HasConnection`][sunflare.virtual.HasConnection] protocol)
  - [`SenderReceiver`][sunflare.presenter.SenderReceiver] (union of previous two mixins)

## API Reference

::: sunflare.presenter
    options:
      show_root_heading: true
      show_source: true
      members_order: source
