# 1EcoDesign Heatpumps

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![release](https://img.shields.io/github/v/release/itsh-neumeier/modbus_1ecodesign-heatpump)](https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases)

German documentation: [README.de.md](README.de.md)
`README.de.md` is maintained as an up-to-date translated derivative of this file.

HACS-compatible Home Assistant custom integration for 1EcoDesign heat pumps
(ED300KWL / VC200 family) via Modbus TCP.

## Features

- Native Home Assistant integration (not based on automations/scripts)
- Async Modbus TCP communication (`pymodbus`)
- Config Flow setup from UI
- Fast and efficient polling using grouped register reads
- Control and monitoring entities:
  - Sensors
  - Binary Sensors
  - Numbers (setpoints)
  - Selects (modes)
  - Switches (on/off controls)
- Security and quality checks in CI

## Compatibility

- Home Assistant: `2024.8.0+`
- Protocol: Modbus TCP
- Tested slave ID: `3` (responding)

## Installation (HACS)

1. Open HACS -> Integrations.
2. Add custom repository:
   `https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump`
   as category `Integration`.
3. Install **1EcoDesign Heatpumps**.
4. Restart Home Assistant.
5. Go to Settings -> Devices & Services -> Add Integration.
6. Select **1EcoDesign Heatpumps**.

## Manual Installation

1. Copy `custom_components/modbus_1ecodesign_heatpump` to your Home Assistant
   `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration from UI (Settings -> Devices & Services).

## Configuration

During setup, provide:

- `Host` (example: `192.168.73.42`)
- `Device profile` (model-specific register mapping)
- `Port` (default: `502`)
- `Modbus slave ID` (default: `3`)
- `Polling interval` in seconds
- `Timeout` in seconds
- Optional integration name

The integration performs a real Modbus read check before saving config.

### Device Profiles

The integration now ships profile YAML files in
`custom_components/modbus_1ecodesign_heatpump/device_profiles/`.
Supported dropdown profiles:

- `ED300KWL`
- `ED100KWL`
- `ED100WL`
- `ED180WL`
- `ED180P`
- `ED100RF`
- `Froeling BWP300PV (OEM)`

Findings from uploaded manuals:

- The common holding/input register map is largely identical across
  `ED100KWL`, `ED100WL`, `ED180WL`, `ED180P`, and `ED300KWL`.
- `ED100RF` has swapped sensor semantics for input register `7/8` (`T1/T2`);
  this is handled through profile overrides.
- `ED compact power` manual did not expose a compatible Modbus register chapter,
  so it is not added as selectable profile yet.

## Entity Mapping (core set)

### Sensors

- `T1 Evaporator Temperature` (Input Register 7, scale 0.1 degC)
- `T2 Tank Temperature` (Input Register 8, scale 0.1 degC)
- `Remaining Holiday Days` (Input Register 17)
- `Status Bits` (Input Register 16)
- `Unit Alarm Bits` (Input Register 18)
- `Firmware Version` (Input Register 119, scale 0.1)

### Binary Sensors

- `DI1 Pressostat` (0)
- `DI2 PV Input` (1)
- `Relay Compressor` (9)
- `Relay Electric Heater` (10)
- `Relay Boiler` (11)
- `Relay Solenoid Valve` (12)
- `Relay Condenser` (13)
- `Relay Fan` (14)

`Status` and `Unit Alarm` stay single sensor entities (`status_bits`, `unit_alarm_bits`).
State contains decoded text flags; `active_flags` and `raw_value` are exposed as attributes.

### Number Controls

- `Water Setpoint` (Holding Register 4)
- `T min` (5)
- `T2 min` (6)
- `PV HP Setpoint` (18)
- `PV EL Setpoint` (19)
- `T max` (28)
- `Legionella Cycle Days` (33)
- `Manual Holiday Days` (21)
- `EC Fan Level 1/2/3` (30/31/32)

### Select Controls

- `Heating Mode` (12)
- `Legionella Function` (13)
- `Fan Operation` (15)
- `Ventilation Control` (16)
- `PV Mode` (17)
- `Holiday Mode` (20)
- `Fan Pause` (23)
- `Language` (25)
- `Defrost Mode` (26)
- `Fan Type` (29)

### Switch Controls

- `Timer Enabled` (7)
- `Boost Enabled` (22)
- `Anode Enabled` (27)

### Time Controls

- `Timer Start` (Holding Registers 8+9 as HH:MM)
- `Timer Stop` (Holding Registers 10+11 as HH:MM)

### Gateway Monitoring

- A dedicated `Modbus TCP Gateway` device is created in the device registry.
- Heatpump device is linked as `connected via` this gateway device.
- `Gateway Online` binary sensor reports TCP reachability of the converter endpoint.

## Performance Notes

- Register reads are grouped into contiguous blocks.
- One coordinator serves all entities.
- Client connection is reused and reconnected only when needed.
- Polling defaults to 15 seconds and can be tuned in options.

## Security Notes

- Local polling only, no cloud account required.
- CI checks:
  - `hassfest`
  - `ruff`
  - `bandit`
  - `pip-audit`
- Dependency updates handled by Dependabot.

Current baseline scans are expected to be clean for this repository version.

## Example Automations

### PV surplus control for Victron MPPT RS450/200 (event-driven, no time pattern)

This example is tailored to a Victron MPPT RS450/200 setup.
Adjust entity IDs to your Victron integration naming.

```yaml
alias: "PV Control: Heatpump PV Mode"
mode: single
triggers:
  - id: mpp1_limited
    trigger: state
    entity_id: sensor.victron_solarcharger_mppoperationmode_1
    to: "LIMITED"
    for: "00:00:10"
  - id: mpp2_limited
    trigger: state
    entity_id: sensor.victron_solarcharger_mppoperationmode
    to: "LIMITED"
    for: "00:00:10"
  - id: excess_lost
    trigger: template
    value_template: >-
      {{
        states('sensor.victron_battery_soc')|float(0) <= 90
        or (
          states('sensor.victron_solarcharger_mppoperationmode_1') != 'LIMITED'
          and states('sensor.victron_solarcharger_mppoperationmode') != 'LIMITED'
        )
      }}
    for: "00:05:00"
conditions: []
actions:
  - choose:
      - conditions:
          - condition: template
            value_template: "{{ trigger.id in ['mpp1_limited', 'mpp2_limited'] }}"
          - condition: numeric_state
            entity_id: sensor.victron_battery_soc
            above: 90
          - condition: or
            conditions:
              - condition: state
                entity_id: sensor.victron_solarcharger_mppoperationmode_1
                state: "LIMITED"
              - condition: state
                entity_id: sensor.victron_solarcharger_mppoperationmode
                state: "LIMITED"
          - condition: not
            conditions:
              - condition: state
                entity_id: select.froling_bwp300pv_betriebsmodus_pv_sg
                state: "hp_plus_el"
        sequence:
          - service: select.select_option
            target:
              device_id: 39ab34012f47b248e4714f7e2f381909
              entity_id: select.froling_bwp300pv_betriebsmodus_pv_sg
            data:
              option: "hp_plus_el"
      - conditions:
          - condition: template
            value_template: "{{ trigger.id == 'excess_lost' }}"
          - condition: state
            entity_id: select.froling_bwp300pv_betriebsmodus_pv_sg
            state: "hp_plus_el"
            for: "00:30:00"
        sequence:
          - service: select.select_option
            target:
              device_id: 39ab34012f47b248e4714f7e2f381909
              entity_id: select.froling_bwp300pv_betriebsmodus_pv_sg
            data:
              option: "off"
```

### Night quiet mode (lower fan)

```yaml
automation:
  - alias: Heatpump Night Fan Level
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: select.select_option
        target:
          entity_id: select.heatpump_fan_operation
        data:
          option: "EC Low"
```

## Versioning & Release

- This repository uses [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html).
- Create a new version by:
  1. Update version in
     `custom_components/modbus_1ecodesign_heatpump/manifest.json`
  2. Update `CHANGELOG.md`
  3. Commit and tag: `vX.Y.Z`
  4. Push commit and tag to GitHub
- GitHub workflow validates manifest/tag version match.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT - see [LICENSE](LICENSE).
