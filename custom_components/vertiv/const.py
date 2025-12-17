"""Constants for the Vertiv PowerAssist integration."""

from __future__ import annotations

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "vertiv"

PLATFORMS: Final = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

DEFAULT_NAME: Final = "Vertiv UPS"
DEFAULT_PORT: Final = 8210
API_ENDPOINT: Final = "/api/PowerAssist"

SCAN_INTERVAL_SECONDS: Final = 20
REQUEST_TIMEOUT: Final = 20

KEY_UNIQUE_ID: Final = "upsUniqueIdentifier"
KEY_MODEL: Final = "modelNumber"
KEY_FIRMWARE_VERSION: Final = "version"
STATUS_KEY: Final = "status"

KEY_RUN_TIME: Final = "runTimeToEmptyInSeconds"
KEY_CAPACITY: Final = "remainingCapacityInPercent"
KEY_BATTERY_VOLTAGE: Final = "batteryVoltage"
KEY_PERCENT_LOAD: Final = "percentLoad"
KEY_INPUT_VOLTAGES: Final = "inputVoltages"
KEY_OUTPUT_VOLTAGES: Final = "outputVoltages"

KEY_IS_AC_PRESENT: Final = "isAcPresent"
KEY_IS_CHARGING: Final = "isCharging"
KEY_IS_DISCHARGING: Final = "isDischarging"
KEY_NEEDS_REPLACEMENT: Final = "needsReplacement"
KEY_IS_OVERLOAD: Final = "isOverload"
KEY_IS_UPS_ON: Final = "isUpsOn"
KEY_LOW_CAPACITY_LIMIT: Final = "belowRemainingCapacityLimit"

STATE_ONLINE: Final = "Online"
STATE_ON_BATTERY: Final = "On Battery"
STATE_CHARGING: Final = "Charging"
STATE_DISCHARGING: Final = "Discharging"
STATE_REPLACEMENT_NEEDED: Final = "Battery Needs Replacement"
STATE_OVERLOAD: Final = "Overload"
STATE_OFFLINE: Final = "Offline"

KEY_SHUTDOWN_TYPE: Final = "shutdownType"
KEY_BATT_TIME_MIN: Final = "batteryTimeRemainingMinutes"
KEY_BATT_CAPACITY_PERCENT: Final = "batteryCapacityPercent"
KEY_AFTER_X_MINUTES: Final = "afterXMinutes"
KEY_SHUTDOWN_IF_ALL: Final = "shutdownIfAllUpsLosesPower"
KEY_MAINTENANCE_MODE_POST: Final = "maintenanceModeActive"
KEY_MAINTENANCE_MODE_GET: Final = "maintenanceModeActive_get"
KEY_ENABLE_SCRIPTED_SHUTDOWN: Final = "enableScriptedShutdown"
KEY_SCRIPTED_SHUTDOWN_PATH: Final = "scriptedShutdownFilePath"


SHUTDOWN_TYPE_OPTIONS: Final = {
    0: "By Battery Minutes Remaining",
    1: "By Battery Percent Remaining",
    2: "After X Minutes",
    3: "Immediately",
}
