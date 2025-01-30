# Statement of need

The goal of sunflare is to provide shared and recognizable programming patterns accross the entire Redsun ecosystem.
As Redsun heavy leverages the concept of plugins, there is a need to provide a clear representation and communication channel between all the plugins that in the end build the desired application.

```{figure} _static/dark/redsun_ecosystem.png
:alt: Redsun ecosystem
:name: ecosystem
:align: center
:class: img-theme-switch

Redsun ecosystem relationship
```

{numref}`ecosystem` shows the relationship between Redsun, Sunflare and the custom plugins. Effectively, Redsun is nothing more than "glue" code that allows your custom application. What it does is:

- retrieve the user plugins via [Python entry points];
- build said plugins and catch any possible exception throw by them;
- build the final application and connecting all the plugins together.

This approach ensures that Sunflare can be reused as a standalone package to provide reusable code pieces to write effective control interfaces for your device which fit the Bluesky message protocol and data model.
Furthermore, if you have an existing package for hardware control, Sunflare allows to create a wrapper for your classes which can then "talk" the Bluesky language.

[python entry points]: https://packaging.python.org/en/latest/specifications/entry-points/
