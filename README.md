# Vertiv PowerAssist for Home Assistant

[![hacs][hacsbadge]][hacs]
[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![Project Maintenance][maintenance-shield]][user_profile]
[![License][license-shield]][license]
[![pre-commit][pre-commit-shield]][pre-commit]

A lightweight, local integration that surfaces status from Vertiv UPS devices via the Vertiv PowerAssist service and lets you control how and when your system should shut down during a power event.

## Overview
- Local-only: Talks directly to your PowerAssist instance on your network
- Clean entities: Battery, runtime, load, input/output voltages, and key health flags
- Practical controls: Configure shutdown behavior to match your environment (details below)

## Requirements
- Vertiv PowerAssist running on a reachable host
  - Tested with PowerAssist 2.0.0 on an Arch‑based Linux host

Behavior may differ across UPS models or multi‑UPS environments.

## Installation
1. Copy this folder to `config/custom_components/vertiv` and restart Home Assistant.
2. In Home Assistant, go to Settings → Devices & Services → Add Integration → search for “Vertiv PowerAssist”.
3. Provide host and port for the machine running PowerAssist.

## Configuration
During setup you’ll be asked for:
- Hostname or IP of the PowerAssist machine
- Port (default: 8210, unless you changed it)
- Device name

After setup, you can fine‑tune shutdown behavior from the Vertiv device page in Home Assistant.

## What You Get
- UPS status at a glance
  - AC power present, charging/discharging state, overload, battery health
  - Battery capacity (%), runtime to empty (seconds), output load (%), input/output voltages
- Configurable shutdown behavior
  - Shutdown Mode (select):
    - By Battery Minutes Remaining
    - By Battery Percent Remaining
    - After X Minutes
    - Immediately
  - Matching parameter values (numbers/switches):
    - Minutes threshold (for “By Minutes”)
    - Capacity threshold in % (for “By Percent”)
    - Delay value in minutes (for “After X Minutes”)
    - Shut down only if all UPS lose power (toggle)
    - Maintenance mode (toggle)
    - Optional scripted shutdown (toggle + path)

## Entities
- Sensors
  - Runtime remaining (seconds)
  - Battery capacity (%)
  - Battery voltage (V)
  - Output load (%)
  - Input voltage (V)
  - Output voltage (V)
- Binary sensors
  - AC power present, charging, on battery, battery needs replacement, overload, UPS running, battery low limit reached
- Select
  - Shutdown trigger type (mode)
- Numbers
  - Battery time threshold (minutes), battery capacity threshold (%), shutdown after X minutes
- Switches
  - Maintenance mode, shutdown if all UPS lose power, enable scripted shutdown

## Notes & Limitations
- Integration assumes PowerAssist is reachable over HTTPS with a self‑signed certificate (default configuration in PowerAssist); the client is configured accordingly.
- Reported fields and flags can vary by UPS model/firmware.
- Multi‑UPS setups may expose combined settings (e.g., "shutdown if all lose power").

## Troubleshooting
- Can’t connect during setup
  - Verify host/port and that PowerAssist is running and reachable from Home Assistant.

## Credits
- Vertiv PowerAssist provides the local API this integration communicates with.
- Community inspiration from Home Assistant’s update coordinator and modern entity patterns.

<!-- Badges & links -->
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs]: https://github.com/hacs/integration
[releases-shield]: https://img.shields.io/github/release/bennydiamond/vertiv_powerassist.svg
[releases]: https://github.com/bennydiamond/vertiv_powerassist/releases
[commits-shield]: https://img.shields.io/github/commit-activity/m/bennydiamond/vertiv_powerassist.svg
[commits]: https://github.com/bennydiamond/vertiv_powerassist/commits
[maintenance-shield]: https://img.shields.io/badge/maintained-yes-brightgreen.svg
[user_profile]: https://github.com/bennydiamond
[license-shield]: https://img.shields.io/github/license/bennydiamond/vertiv_powerassist.svg
[license]: https://github.com/bennydiamond/vertiv_powerassist/blob/master/LICENSE.md
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
[pre-commit]: https://pre-commit.com/
