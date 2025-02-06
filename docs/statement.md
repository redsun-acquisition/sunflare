# Statement of need

The goal of Sunflare is to provide shared and recognizable programming patterns accross the entire Redsun ecosystem.
As Redsun heavily leverages the concept of plugins, there is a need to provide a clear representation and a shared communication channel between the plugins that in the end build the desired application.

```mermaid
:config: {"theme": "base"}
:align: center
%%{init: { 'theme': 'base', 'themeVariables': { 'primaryColor': '#fefefe', 'lineColor': '#aaa000', } } }%%
    graph TD
        Sunflare -->|builds| Plugins
        Sunflare -->|builds| Redsun
        Plugins -->|used in| Redsun
```

The diagram shows the relationship between Redsun, Sunflare and the custom plugins. Effectively, Redsun is nothing more than "glue" code that allows your custom application. What it does is:

- retrieve the user plugins via [Python entry points];
- build said plugins and catch any possible exception throw by them;
- build the final application and connecting all the plugins together.

This approach ensures that Sunflare can be reused as a standalone package to provide reusable code to create custom control interfaces for your device, which fit the Bluesky [message protocol] and [data model].

Furthermore, if you have an existing package for hardware control, Sunflare can be used to create a wrapper for your classes which can then "talk" the Bluesky language.

[python entry points]: https://packaging.python.org/en/latest/specifications/entry-points/
[message protocol]: https://blueskyproject.io/bluesky/main/msg.html
[data model]: https://blueskyproject.io/event-model/main/explanations/data-model.html
