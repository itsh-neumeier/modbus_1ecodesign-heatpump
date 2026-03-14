# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog, and this project follows
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [0.1.7] - 2026-03-14

### Changed
- Added global translation titles (`title`) like Home Assistant translation examples:
  - DE: `1EcoDesign Wärmepumpen`
  - EN: `1EcoDesign Heatpumps`
- Added fallback title in `strings.json`.

## [0.1.6] - 2026-03-14

### Changed
- Updated multilingual config-flow titles:
  - DE: `1EcoDesign Wärmepumpen`
  - EN: `1EcoDesign Heatpumps`
- Added integration branding images from 1EcoDesign favicon:
  - `custom_components/modbus_1ecodesign_heatpump/icon.png`
  - `custom_components/modbus_1ecodesign_heatpump/logo.png`

## [0.1.5] - 2026-03-14

### Added
- Implemented decoded bit sensors for `Status` (Input Register 16).
- Implemented decoded bit sensors for `Unit Alarm` (Input Register 18).
- Added EN/DE translation keys for all new bit sensors.

### Changed
- Updated EN/DE documentation to describe new status/alarm bit entities.

## [0.1.4] - 2026-03-14

### Fixed
- Added compatibility for multiple `pymodbus` 3.x APIs (`device_id` and legacy `slave`).
- Fixed config-flow submit crash that appeared as `Unexpected error`.
- Added exception logging in config validation to simplify troubleshooting.

## [0.1.3] - 2026-03-14

### Fixed
- Prevented config-flow import crash by lazy-loading Modbus dependencies.
- Added explicit user-facing error if Python dependency is missing.
- Relaxed `pymodbus` requirement to improve installation compatibility.

## [0.1.2] - 2026-03-14

### Fixed
- Fixed manifest key ordering to satisfy hassfest validation.
- Removed unused `async_setup` to avoid config schema warning for entry-only setup.

## [0.1.1] - 2026-03-14

### Changed
- Updated all repository URLs to the published GitHub repository.
- Improved CI trigger to run on all pushes.

## [0.1.0] - 2026-03-14

### Added
- Initial HACS compatible Home Assistant integration.
- Async Modbus TCP client with reconnect handling.
- Config Flow with connection test.
- Platforms: sensor, binary_sensor, number, select, switch.
- Polling with grouped register reads for performance.
- EN and DE documentation.
- GitHub CI: hassfest, linting, bandit, pip-audit, release-on-tag.
- Dependabot and security policy.

[0.1.7]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.7
[0.1.6]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.6
[0.1.5]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.5
[0.1.4]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.4
[0.1.3]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.3
[0.1.2]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.2
[0.1.1]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.1
[0.1.0]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.0
