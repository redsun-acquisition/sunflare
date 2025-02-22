# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Dates are specified in the format `DD-MM-YYYY`.

## [0.4.0] - 22-02-2025

### Added

- Implemented support for ZMQ messaging via `pyzmq`
- Added initial support for `msgspec`
- Added mixin classes for creating publisher/subscribers
- Added mixin classes for `Signal`-enabled controllers
- Added more documentation for the virtual module
- Reorganized code in different modules to avoid circular imports
- Split controller in different protocols
- Added `ModelInfoProtocol` to deploy models from packages that don't have a strict dependency with Sunflare
- Added more tests, both for existing and new code

## [0.3.5] - 11-02-2025

### Added

- Added protocol equivalent for `ModelInfo`
  - Currently untested
  - This can be used in combination with `ModelProtocol` to define a Model interface from an external package without direct dependency to the `sunflare` package.
- Added documentation for `Controller`
- Added tests for `RunEngine` wrapper

### Changed

- Minor docstring and renaming fixes
- `engine` and `frontend` fields of `RedSunSessionInfo` are not optional anymore

### Fixed

- `RunEngine.__call__` fails in Python 3.9 unless explictly setting the event loop in the executor

## [0.3.4] - 05-02-2025

### Fixed

- Fixed bug in `RedSunSessionInfo.store_yaml` which was not correctly parsing `Enum` and `tuple` types

## [0.3.3] - 04-02-2025

### Changed

- Minor renaming
  - RedSun -> Redsun
  - SunFlare -> Sunflare

### Added

- Added documentation
  - Notions of O.O.P.
  - Minimal model doc
- Added test for VirtualBus connection mechanism
- Added `WidgetInfo` class
  - Provides information for widgets
  - Redsun uses it to correctly allocate dock widgets in the main view
  - Currently adapted to be used with `PyQt` and `PySide`
    - For web-based frameworks may require adjustments somehow
- Added `RedSunSessionInfo.store_yaml` to save the configuration file elsewhere
  - We **could** think of supporting dynamic plugin loading; this would mean changing the content of `RedSunSessionInfo` on the fly.

## [0.3.2] - 29-01-2025

### Added

- `session` field in `RedSunSessionInfo`
  - used as main window title and as bluesky metadata
- added `**kwargs` to `configure` method
  - need investigation on how to actually use it
- added optional `shutdown` method in `ModelProtocol`
  - it still must be implemented although not mandatory

### Removed
- removed built-in protocols `Detector` and `Motor`
  - each plugin should take care of deciding what they are

### Changed
- fixed metaclass error in `BaseQtWidget`

## [0.3.1] - 27-01-2025

### Added

- Added parts of `Configurable` protocol in `ModelInfo` for easier handling

## [0.3.0] - 27-01-2025

### Changed 

- Refactor: simplify `virtual` module and remove `EngineHandler`
- Use `typing_extensions.Protocol` in case of `Python < 3.11`

### Added

- Added a wrapper of `RunEngine` which leaves the main thread unblocked

## [0.2.2] - 02-01-2025

### Changed

- Correct engine handler API.
- Update CI action versions.

## [0.2.1] - 02-01-2025

### Changed

- Engine handler now stores plans as dictionary of dictionaries.
  - The key of the main dictionary is the controller name which holds the plans;
  - The values are dictionaries:
    - Keys are the plan names;
    - Values are plans built with `functools.partial`

## [0.2.0] - 31-12-2024

### Added

* Change configuration classes to use attrs in https://github.com/redsun-acquisition/sunflare/pull/8
* Model API rework in https://github.com/redsun-acquisition/sunflare/pull/9

## [0.1.1] - 26-12-2024

- Same changes as [v0.1.1a1]
- Some typo adjustments

## [0.1.1a1] - 25-12-2024

(Only available on TestPyPI)

### Added

- Rework handler by @jacopoabramo in [#6](https://github.com/redsun-acquisition/sunflare/pull/6)
- Reworked a lot of logic
  - Models are now subclassed in Models for easier type hinting management
  - Using RedSunInstanceInfo in handler
  - RedSunInstance info now holds logic to load and check yaml file as static method

## [0.1.0] - 23-12-2024

### Added

- First release on PyPI;
- Reached above 90% coverage;

## [0.1.0a1] - 22-12-2024

(Only available on TestPyPI)

### Added

- Alpha release;
- Basic project infrastructure;

[0.4.0] https://github.com/redsun-acquisition/sunflare/compare/v0.3.5...0.4.0
[0.3.5]: https://github.com/redsun-acquisition/sunflare/compare/v0.3.4...v0.3.5
[0.3.4]: https://github.com/redsun-acquisition/sunflare/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/redsun-acquisition/sunflare/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/redsun-acquisition/sunflare/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/redsun-acquisition/sunflare/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/redsun-acquisition/sunflare/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/redsun-acquisition/sunflare/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/redsun-acquisition/sunflare/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/redsun-acquisition/sunflare/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/redsun-acquisition/sunflare/compare/v0.1.0...v0.1.1
[0.1.1a1]: https://github.com/redsun-acquisition/sunflare/compare/v0.1.0...v0.1.1a1
[0.1.0]: https://github.com/redsun-acquisition/sunflare/compare/v0.1.0a1...v0.1.0
[0.1.0a1]: https://github.com/redsun-acquisition/sunflare/commits/v0.1.0a1/
