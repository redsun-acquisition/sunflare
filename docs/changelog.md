# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Dates are specified in the format `DD-MM-YYYY`.

## [Unreleased]

### Changed

- Synchronize all dependencies correctly via `uv`
- Bump `bluesky` version to `1.14.5`
  - Fix type hints accordingly
- Trigger CI for docs deployment and PyPI publishing from GitHub release page
  - Previously new tag had to be manually pushed from CLI

## [0.6.1] - 04-07-2025

### Fixed

- Inject `ViewInfoProtocol` and not the base class in the view base classes

## [0.6.0] - 04-07-2025

### Added

- Added `sunflare.containers` module for dynamically registering protocols and plans
  - Provided 4 functions
    - `register/get_plans`
    - `register/get_protocols`
  - Plan signatures are unwrapped within `PlanSignature` dataclass object
    - The signatures can be retrieved via `get_signatures`
  - Registered plans must be type annotated to be correctly registered and used by other plugins
- Added initial testing

### Changed

- Dropped support for 3.9
- Removed usage of `Optional` and `Union`
  - Replaced with built-in `|` instead
- Switch to `uv` for dependency management
  - Added `uv.lock` file
- Removed `engine` field from `RedsunSessionInfo`
  - Not really meaningful, was part of old concept
- Renamed `Widget` components to `View`
- Ex-`Widget` classes are now injected with `ViewInfo` in initializer rather than `RedSunSessionInfo`

## [0.5.5] - 02-04-2025

### Fixed

- catch exception when `RunEngine.stop()` is called from main thread

## [0.5.4] - 31-03-2025

### Fixed

- fixed `msgspec` decoding hook
  - now returns the object when it's not of type `np.ndarray`
- fixed `RunEngine` document emission
  - `emit` was failing to parse the document name

## [0.5.3] - 25-03-2025

### Changed

- Reworked `log.py`
  - When calling `obj.debug`, the line where the call was emitted redirected to `Loggable`
  - using a `logging.LoggerAdapter` prevents this
  - it also make the usage of `Loggable` more consistent by simply returning a `cached_property`, which now enforces usage of `obj.logger.debug` which is less confusing

## [0.5.2] - 13-03-2025

### Changed

- Enhanced `sunflare.log` in order to separate log calls between two handlers.

## [0.5.1] - 06-03-2025

### Changed

- Dropped upper bound limit for `numpy` dependency

## [0.5.0] - 03-03-2025

### Changed

- Rearranged the structure of virtual-related classes
  - Everything related to creating connections with the virtual bus have been brought to the `sunflare.virtual` module
- Set the default log level to `INFO` (was `DEBUG` before)
- Reworked `sunflare.config` to accomodate for new plugin system

### Added

- Added a `Model` base class for quicker development.

### Removed

- `configure` protocol is not part of the `ModelProtocol` anymore; see [this PR](https://github.com/bluesky/bluesky/pull/1888)

## [0.4.2] - 24-02-2025

### Changed

- Changed `ModelProtocol.configure` signature
  - Previous signature was not consistent with the command issued by the `RunEngine`

## [0.4.1] - 23-02-2025

### Added

- Added support for `Mapping` types (i.e. `dict`) in `ModelInfo` methods (`read/describe_configuration`)
- Added optional parameters for `read/describe_configuration`
  - `read_configuration`: `timestamp` (i.e. use `time.time()` for a timestamp of the last reading time)
  - `describe_configuration`: `source`, to specify the source of the configuration parameter

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

[0.6.1]: https://github.com/redsun-acquisition/sunflare/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/redsun-acquisition/sunflare/compare/v0.5.5...v0.6.0
[0.5.5]: https://github.com/redsun-acquisition/sunflare/compare/v0.5.4...v0.5.5
[0.5.4]: https://github.com/redsun-acquisition/sunflare/compare/v0.5.3...v0.5.4
[0.5.3]: https://github.com/redsun-acquisition/sunflare/compare/v0.5.2...v0.5.3
[0.5.2]: https://github.com/redsun-acquisition/sunflare/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/redsun-acquisition/sunflare/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/redsun-acquisition/sunflare/compare/v0.4.2...v0.5.0
[0.4.2]: https://github.com/redsun-acquisition/sunflare/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/redsun-acquisition/sunflare/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/redsun-acquisition/sunflare/compare/v0.3.5...v0.4.0
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
