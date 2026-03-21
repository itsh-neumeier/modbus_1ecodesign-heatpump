# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog, and this project follows
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [0.2.4] - 2026-03-21

### Added
- Added reusable Home Assistant blueprint for Victron MPPT RS450/200 PV
  surplus control:
  `blueprints/automation/itsh_neumeier/victron_mppt_rs450_200_pv_surplus_heatpump.yaml`

### Changed
- Replaced the long README automation example with blueprint-based usage
  instructions in `README.md` and `README.de.md`.

## [0.2.3] - 2026-03-15

### Added
- Added writable number entity `legionella_cycle_days` (Holding Register `33`,
  range `3..14`) to configure legionella auto-cycle interval.

### Changed
- Updated EN/DE documentation and translations for the new legionella cycle
  setting.

## [0.2.2] - 2026-03-15

### Changed
- Updated Victron PV surplus automation examples in `README.md` and
  `README.de.md` to use Fröling BWP300PV targets:
  - entity: `select.froling_bwp300pv_betriebsmodus_pv_sg`
  - device_id: `39ab34012f47b248e4714f7e2f381909`

## [0.2.1] - 2026-03-15

### Changed
- `holiday_mode` select entity is now enabled by default
  (no longer disabled in the entity registry).

## [0.2.0] - 2026-03-15

### Added
- Implemented native timer control entities:
  - `time.timer_start` (Registers 8+9)
  - `time.timer_stop` (Registers 10+11)
- Added profile-based timer register configuration in all device profiles.
- Added dedicated `Modbus TCP Gateway` device with `Gateway Online`
  diagnostic binary sensor.
- Linked heatpump device to the gateway device using device registry
  `via_device` (`connected via` in UI).

### Changed
- Added batch write support for multiple holding registers to ensure coherent
  timer writes (hour+minute together).

### Migration
- Added config-entry migration to version `3` to ensure existing installations
  get a default `device_profile` in both entry data and options.

## [0.1.16] - 2026-03-15

### Changed
- Increased leaf icon visual size across all icon variants for better visibility
  in Home Assistant and HACS cards:
  - `custom_components/modbus_1ecodesign_heatpump/brand/icon*.png`
  - `custom_components/modbus_1ecodesign_heatpump/*icon*.png`
  - repository root `brand/icon*.png`

## [0.1.15] - 2026-03-15

### Changed
- Added optimized event-driven PV surplus automation example to README files
  (replaces `time_pattern` polling approach).
- Marked the example explicitly for `Victron MPPT RS450/200`.
- Added note to adapt Victron entity IDs to local setup naming.

## [0.1.14] - 2026-03-15

### Added
- Added repository-root `brand/` assets for improved HACS logo discovery:
  - `brand/icon.png`, `brand/logo.png`, `brand/dark_icon.png`, `brand/dark_logo.png`
  - `brand/icon@2x.png`, `brand/logo@2x.png`,
    `brand/dark_icon@2x.png`, `brand/dark_logo@2x.png`

### Verified
- Full translation parity check passed:
  - `strings.json` == `translations/en.json` == `translations/de.json`
  - all `translation_key` values used in code are present in translations

## [0.1.13] - 2026-03-15

### Changed
- Standardized README naming and presentation:
  - title set to `1EcoDesign Heatpumps`
  - added HACS/License/Release badges
  - removed endpoint-specific tested host from docs
  - replaced setup host example with randomized private LAN example
- Linked German README from default README and documented that
  `README.de.md` is maintained as an up-to-date translated derivative.
- Added branding compatibility assets to improve icon/logo visibility across
  Home Assistant/HACS variants:
  - root-level `icon.png`, `logo.png`, `dark_icon.png`, `dark_logo.png`
  - `brand/icon@2x.png`, `brand/logo@2x.png`, `brand/dark_icon@2x.png`,
    `brand/dark_logo@2x.png`

## [0.1.12] - 2026-03-15

### Added
- Added external YAML-based device profiles under
  `custom_components/modbus_1ecodesign_heatpump/device_profiles/`.
- Added profile selector dropdown to config flow and options flow.
- Added selectable profiles:
  - `ED300KWL`
  - `ED100KWL`
  - `ED100WL`
  - `ED180WL`
  - `ED180P`
  - `ED100RF`
  - `Froeling BWP300PV (OEM)`

### Changed
- Aligned HACS/Home Assistant display title to integration title:
  - `manifest.json` name -> `1EcoDesign Heatpumps`
  - `hacs.json` name -> `1EcoDesign Heatpumps`
- Updated manifest metadata quality and ownership:
  - `codeowners` -> `@itsh-neumeier`
  - added `integration_type: hub`
  - added `quality_scale: bronze`
- Device `manufacturer` / `model` are now profile-driven in device info.
- Device page `configuration_url` now always targets HTTP port `80`.
- Entity setup now supports profile-based per-entity overrides/exclusions.
- Updated integration branding from official 1EcoDesign logo with transparent
  light/dark assets:
  - `brand/logo.png`
  - `brand/dark_logo.png`
  - `brand/icon.png`
  - `brand/dark_icon.png`
- Added compatibility branding fallbacks:
  - root-level `icon.png` / `logo.png` / `dark_icon.png` / `dark_logo.png`
  - `brand/*@2x.png` variants
- Added RF-specific mapping override:
  - `T1/T2` input-register assignment adjusted for `ED100RF` manuals.
  - AC fan operation option states added for `ED100RF`.

## [0.1.11] - 2026-03-14

### Changed
- Added translated select option values (state translations) for EN/DE
  (e.g. heating modes, PV mode, fan modes, defrost mode).
- Localized `status_bits` and `unit_alarm_bits` decoded values for EN/DE.

## [0.1.10] - 2026-03-14

### Changed
- `status_bits` and `unit_alarm_bits` now output decoded flag texts as sensor state
  (no numeric state output).
- Added `raw_value` attribute so the original register value is still available.

## [0.1.9] - 2026-03-14

### Changed
- Implemented Home Assistant local integration branding layout under:
  `custom_components/modbus_1ecodesign_heatpump/brand/`
- Moved branding files to:
  - `brand/icon.png`
  - `brand/logo.png`
- Added dark-mode branding fallbacks:
  - `brand/dark_icon.png`
  - `brand/dark_logo.png`

## [0.1.8] - 2026-03-14

### Changed
- Device manufacturer set to `1EcoDesign GmbH`.
- Entity names moved to translation-based naming (EN/DE).
- Status and Unit Alarm are each a single sensor entity (not binary-sensor bit fanout).
- Status/Alarm decoding texts use YAML-style labels and are provided via `active_flags`.
- Advanced entities that should not be changed by default are disabled in registry by default.

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

[0.2.4]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.2.4
[0.2.3]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.2.3
[0.2.2]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.2.2
[0.2.1]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.2.1
[0.2.0]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.2.0
[0.1.16]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.16
[0.1.15]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.15
[0.1.14]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.14
[0.1.13]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.13
[0.1.12]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.12
[0.1.11]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.11
[0.1.10]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.10
[0.1.9]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.9
[0.1.8]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.8
[0.1.7]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.7
[0.1.6]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.6
[0.1.5]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.5
[0.1.4]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.4
[0.1.3]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.3
[0.1.2]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.2
[0.1.1]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.1
[0.1.0]: https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases/tag/v0.1.0
