# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Dates are specified in the format `DD-MM-YYYY`.


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

[v0.1.1]: https://github.com/redsun-acquisition/sunflare/compare/v0.1.0...v0.1.1
[v0.1.1a1]: https://github.com/redsun-acquisition/sunflare/compare/v0.1.0...v0.1.1a1
[v0.1.0]: https://github.com/redsun-acquisition/sunflare/compare/v0.1.0a1...v0.1.0
[v0.1.0a1]: https://github.com/redsun-acquisition/sunflare/commits/v0.1.0a1/
