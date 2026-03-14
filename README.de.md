# Modbus 1EcoDesign Heatpump

HACS-kompatible Home-Assistant-Custom-Integration fuer 1EcoDesign
Waermepumpen (ED300KWL / VC200) ueber Modbus TCP.

## Funktionen

- Echte native Home-Assistant-Integration (keine Script/Automation-Loesung)
- Asynchrone Modbus-TCP-Kommunikation (`pymodbus`)
- Config Flow (UI-Setup)
- Performantes Polling mit gebuendelten Register-Reads
- Entitaeten:
  - Sensor
  - Binary Sensor
  - Number
  - Select
  - Switch
- Security- und Qualitaetspruefungen per CI

## Kompatibilitaet

- Home Assistant: `2024.8.0+`
- Protokoll: Modbus TCP
- Gepruefter Endpunkt: `192.168.140.217:502`
- Gepruefte Slave-ID: `3`

## Installation (HACS)

1. HACS -> Integrations oeffnen.
2. Custom Repository hinzufuegen:
   `https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump`
   als Kategorie `Integration`.
3. **Modbus 1EcoDesign Heatpump** installieren.
4. Home Assistant neu starten.
5. Unter Settings -> Devices & Services Integration hinzufuegen.

## Manuelle Installation

1. Ordner `custom_components/modbus_1ecodesign_heatpump` in dein
   Home-Assistant-`custom_components` kopieren.
2. Home Assistant neu starten.
3. Integration ueber die UI hinzufuegen.

## Konfiguration

Beim Setup angeben:

- `Host` (z. B. `192.168.140.217`)
- `Port` (Standard `502`)
- `Modbus slave ID` (Standard `3`)
- `Polling interval` in Sekunden
- `Timeout` in Sekunden
- Optional Name

Es wird vor dem Speichern eine echte Modbus-Lesepruefung ausgefuehrt.

## Entitaeten (Kern-Mapping)

### Sensoren

- `T1 Evaporator Temperature` (Input 7, Faktor 0.1)
- `T2 Tank Temperature` (Input 8, Faktor 0.1)
- `Remaining Holiday Days` (Input 17)
- `Status Bits` (Input 16)
- `Unit Alarm Bits` (Input 18)
- `Firmware Version` (Input 119, Faktor 0.1)

### Binary Sensoren

- DI1 Pressostat (0)
- DI2 PV Input (1)
- Relay Compressor (9)
- Relay Electric Heater (10)
- Relay Boiler (11)
- Relay Solenoid Valve (12)
- Relay Condenser (13)
- Relay Fan (14)

`Status` und `Unit Alarm` bleiben je eine einzelne Sensor-Entitaet
(`status_bits`, `unit_alarm_bits`).
Die dekodierten Texte stehen im Attribut `active_flags`.

### Number

- Water Setpoint (Holding 4)
- T min (5)
- T2 min (6)
- PV HP Setpoint (18)
- PV EL Setpoint (19)
- T max (28)
- Manual Holiday Days (21)
- EC Fan Level 1/2/3 (30/31/32)

### Select

- Heating Mode (12)
- Legionella Function (13)
- Fan Operation (15)
- Ventilation Control (16)
- PV Mode (17)
- Holiday Mode (20)
- Fan Pause (23)
- Language (25)
- Defrost Mode (26)
- Fan Type (29)

### Switch

- Timer Enabled (7)
- Boost Enabled (22)
- Anode Enabled (27)

## Performance

- Register werden blockweise gelesen.
- Ein zentraler Coordinator versorgt alle Entitaeten.
- Verbindung wird wiederverwendet und nur bei Bedarf neu aufgebaut.
- Standard-Polling: 15 Sekunden (anpassbar).

## Sicherheit

- Nur lokales Netzwerk, kein Cloud-Zwang.
- CI-Checks:
  - `hassfest`
  - `ruff`
  - `bandit`
  - `pip-audit`
- Dependabot fuer Abhaengigkeiten.

## Beispiele fuer Automatisierungen

### Bei PV Ueberschuss Boost aktivieren

```yaml
automation:
  - alias: Heatpump Boost bei PV
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

### Nachtbetrieb mit niedriger Luefterstufe

```yaml
automation:
  - alias: Heatpump Nachtluefter
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

## Versionierung & Release

- SemVer gemaess [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)
- Pro neue Version:
  1. `manifest.json` Version aktualisieren
  2. `CHANGELOG.md` aktualisieren
  3. Commit + Tag `vX.Y.Z`
  4. Nach GitHub pushen

Der Release-Workflow prueft, ob Tag und Manifest-Version zusammenpassen.

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md).

## Lizenz

MIT - siehe [LICENSE](LICENSE).
