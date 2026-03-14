# Modbus 1EcoDesign Heatpump

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
- Tested endpoint: `192.168.140.217:502` (reachable)
- Tested slave ID: `3` (responding)

## Installation (HACS)

1. Open HACS -> Integrations.
2. Add custom repository:
   `https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump`
   as category `Integration`.
3. Install **Modbus 1EcoDesign Heatpump**.
4. Restart Home Assistant.
5. Go to Settings -> Devices & Services -> Add Integration.
6. Select **Modbus 1EcoDesign Heatpump**.

## Manual Installation

1. Copy `custom_components/modbus_1ecodesign_heatpump` to your Home Assistant
   `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration from UI (Settings -> Devices & Services).

## Configuration

During setup, provide:

- `Host` (example: `192.168.140.217`)
- `Port` (default: `502`)
- `Modbus slave ID` (default: `3`)
- `Polling interval` in seconds
- `Timeout` in seconds
- Optional integration name

The integration performs a real Modbus read check before saving config.

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
Decoded texts are exposed via the `active_flags` attribute.

### Number Controls

- `Water Setpoint` (Holding Register 4)
- `T min` (5)
- `T2 min` (6)
- `PV HP Setpoint` (18)
- `PV EL Setpoint` (19)
- `T max` (28)
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

### PV surplus -> enable boost

```yaml
automation:
  - alias: Heatpump Boost on PV
    trigger:
      - platform: state
        entity_id: binary_sensor.heatpump_di2_pv_input
        to: "on"
        for: "00:05:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.heatpump_boost_enabled
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
