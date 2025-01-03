# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Dates are specified in the format `DD-MM-YYYY`.

## [v0.2.2] - 02-01-2025

### Changed

- Correct engine handler API.
- Update CI action versions.

## [v0.2.1] - 02-01-2025

### Changed

- Engine handler now stores plans as dictionary of dictionaries.
  - The key of the main dictionary is the controller name which holds the plans;
  - The values are dictionaries:
    - Keys are the plan names;
    - Values are plans built with `functools.partial`

## [v0.2.0] - 31-12-2024

### Added

* Change configuration classes to use attrs in https://github.com/redsun-acquisition/sunflare/pull/8
* Model API rework in https://github.com/redsun-acquisition/sunflare/pull/9

## [v0.1.1] - 26-12-2024

- Same changes as [v0.1.1a1]
- Some typo adjustments

## [v0.1.1a1] - 25-12-2024

(Only available on TestPyPI)

### Added

- Rework handler by @jacopoabramo in [#6](https://github.com/redsun-acquisition/sunflare/pull/6)
- Reworked a lot of logic
  - Models are now subclassed in Models for easier type hinting management
  - Using RedSunInstanceInfo in handler
  - RedSunInstance info now holds logic to load and check yaml file as static method

## [v0.1.0] - 23-12-2024

### Added

- First release on PyPI;
- Reached above 90% coverage;

## [v0.1.0a1] - 22-12-2024

(Only available on TestPyPI)

### Added

- Alpha release;
- Basic project infrastructure;

[v0.2.2]: https://github.com/redsun-acquisition/sunflare/compare/v0.2.1...v0.2.2
[v0.2.1]: https://github.com/redsun-acquisition/sunflare/compare/v0.2.0...v0.2.1
[v0.2.0]: https://github.com/redsun-acquisition/sunflare/compare/v0.1.1...v0.2.0
[v0.1.1]: https://github.com/redsun-acquisition/sunflare/compare/v0.1.0...v0.1.1
[v0.1.1a1]: https://github.com/redsun-acquisition/sunflare/compare/v0.1.0...v0.1.1a1
[v0.1.0]: https://github.com/redsun-acquisition/sunflare/compare/v0.1.0a1...v0.1.0
[v0.1.0a1]: https://github.com/redsun-acquisition/sunflare/commits/v0.1.0a1/
