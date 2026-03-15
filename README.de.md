# 1EcoDesign Heatpumps

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)
[![Lizenz: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/itsh-neumeier/modbus_1ecodesign-heatpump)](https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump/releases)

Diese Datei wird als aktuelles, uebersetztes Derivat von `README.md` gepflegt.

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
- Gepruefte Slave-ID: `3`

## Installation (HACS)

1. HACS -> Integrations oeffnen.
2. Custom Repository hinzufuegen:
   `https://github.com/itsh-neumeier/modbus_1ecodesign-heatpump`
   als Kategorie `Integration`.
3. **1EcoDesign Heatpumps** installieren.
4. Home Assistant neu starten.
5. Unter Settings -> Devices & Services Integration hinzufuegen.

## Manuelle Installation

1. Ordner `custom_components/modbus_1ecodesign_heatpump` in dein
   Home-Assistant-`custom_components` kopieren.
2. Home Assistant neu starten.
3. Integration ueber die UI hinzufuegen.

## Konfiguration

Beim Setup angeben:

- `Host` (z. B. `192.168.73.42`)
- `Geraeteprofil` (modellspezifisches Register-Mapping)
- `Port` (Standard `502`)
- `Modbus slave ID` (Standard `3`)
- `Polling interval` in Sekunden
- `Timeout` in Sekunden
- Optional Name

Es wird vor dem Speichern eine echte Modbus-Lesepruefung ausgefuehrt.

### Geraeteprofile

Die Integration nutzt jetzt externe Profil-YAMLs unter
`custom_components/modbus_1ecodesign_heatpump/device_profiles/`.
Auswahl im Dropdown:

- `ED300KWL`
- `ED100KWL`
- `ED100WL`
- `ED180WL`
- `ED180P`
- `ED100RF`
- `Froeling BWP300PV (OEM)`

Ergebnis der Handbuch-Analyse:

- Das Register-Mapping ist bei `ED100KWL`, `ED100WL`, `ED180WL`, `ED180P`
  und `ED300KWL` weitgehend identisch.
- Beim `ED100RF` sind Input-Register `7/8` (`T1/T2`) in der Bedeutung
  vertauscht; das ist jetzt per Profil-Override umgesetzt.
- Im Handbuch `ED compact power` war kein kompatibles Modbus-Registerkapitel
  verifizierbar, daher aktuell noch kein auswaehlbares Profil.

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
Der Zustand enthaelt die dekodierten Flag-Texte; `active_flags` und `raw_value`
stehen zusaetzlich als Attribute zur Verfuegung.

### Number

- Water Setpoint (Holding 4)
- T min (5)
- T2 min (6)
- PV HP Setpoint (18)
- PV EL Setpoint (19)
- T max (28)
- Legionellen-Zyklus Tage (33)
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

### Zeitsteuerung

- `Zeitplanung: Start` (Holding-Register 8+9 als HH:MM)
- `Zeitplanung: Ende` (Holding-Register 10+11 als HH:MM)

### Gateway-Ueberwachung

- Es wird ein eigenes `Modbus TCP Gateway`-Geraet in der Device Registry angelegt.
- Das Waermepumpen-Geraet ist als `connected via` mit diesem Gateway verknuepft.
- Der Binary Sensor `Gateway Online` meldet die TCP-Erreichbarkeit des Converters.

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

### PV-Ueberschusssteuerung fuer Victron MPPT RS450/200 (event-basiert, ohne time_pattern)

Dieses Beispiel ist auf ein Victron-MPPT-RS450/200-Setup ausgelegt.
Bitte die Entity-IDs an deine Victron-Integration anpassen.

```yaml
alias: "PV-Steuerung: BWP PV-Modus"
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
  - id: ueberschuss_weg
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
            value_template: "{{ trigger.id == 'ueberschuss_weg' }}"
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
