"""Device profile helpers for model-specific Modbus mappings."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .const import DEFAULT_DEVICE_PROFILE, DEFAULT_MODEL, MANUFACTURER

_LOGGER = logging.getLogger(__name__)
_PROFILE_DIR = Path(__file__).parent / "device_profiles"


@lru_cache(maxsize=1)
def get_device_profiles() -> dict[str, dict[str, Any]]:
    """Load all YAML device profiles from disk."""
    profiles: dict[str, dict[str, Any]] = {}
    for path in sorted(_PROFILE_DIR.glob("*.yaml")):
        try:
            parsed = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Could not parse device profile: %s", path)
            continue

        if not isinstance(parsed, dict):
            _LOGGER.warning("Ignoring invalid profile file (expected mapping): %s", path)
            continue

        profile_id = str(parsed.get("id") or path.stem).strip()
        if not profile_id:
            _LOGGER.warning("Ignoring profile without id: %s", path)
            continue

        parsed["id"] = profile_id
        parsed.setdefault(
            "name",
            {
                "en": profile_id.upper(),
                "de": profile_id.upper(),
            },
        )
        parsed.setdefault("manufacturer", MANUFACTURER)
        parsed.setdefault("model", DEFAULT_MODEL)
        parsed.setdefault("entity_overrides", {})
        parsed.setdefault("entity_excludes", [])
        parsed.setdefault("timer", {})
        parsed.setdefault("selectable", True)
        profiles[profile_id] = parsed

    if DEFAULT_DEVICE_PROFILE not in profiles:
        profiles[DEFAULT_DEVICE_PROFILE] = {
            "id": DEFAULT_DEVICE_PROFILE,
            "name": {"en": "ED300KWL", "de": "ED300KWL"},
            "manufacturer": MANUFACTURER,
            "model": DEFAULT_MODEL,
            "entity_overrides": {},
            "entity_excludes": [],
            "timer": {},
            "selectable": True,
        }

    return profiles


def get_device_profile(profile_id: str | None) -> dict[str, Any]:
    """Return selected profile or fallback to default profile."""
    profiles = get_device_profiles()
    if profile_id and profile_id in profiles:
        return profiles[profile_id]
    return profiles[DEFAULT_DEVICE_PROFILE]


def get_profile_name(profile: dict[str, Any], language: str | None) -> str:
    """Return localized profile label."""
    names = profile.get("name", {})
    if isinstance(names, dict):
        lang = (language or "en").lower()
        if lang.startswith("de"):
            return str(names.get("de") or names.get("en") or profile["id"])
        return str(names.get("en") or names.get("de") or profile["id"])
    return str(profile["id"])


def get_profile_selector_options(language: str | None) -> list[dict[str, str]]:
    """Build selector options for config flow drop-down."""
    options: list[dict[str, str]] = []
    for profile in get_device_profiles().values():
        if not bool(profile.get("selectable", True)):
            continue
        options.append(
            {
                "value": str(profile["id"]),
                "label": get_profile_name(profile, language),
            }
        )
    options.sort(key=lambda item: item["label"].lower())
    return options


def get_entity_override(profile: dict[str, Any], platform: str, key: str) -> dict[str, Any]:
    """Return per-entity override mapping for a profile."""
    overrides = profile.get("entity_overrides", {})
    if not isinstance(overrides, dict):
        return {}
    platform_overrides = overrides.get(platform, {})
    if not isinstance(platform_overrides, dict):
        return {}
    entity_override = platform_overrides.get(key, {})
    if not isinstance(entity_override, dict):
        return {}
    return entity_override


def is_entity_excluded(profile: dict[str, Any], platform: str, key: str) -> bool:
    """Check if a profile excludes an entity from setup."""
    excludes = profile.get("entity_excludes", [])
    if not isinstance(excludes, list):
        return False
    target = f"{platform}.{key}"
    return any(str(item).strip().lower() == target for item in excludes)


def get_profile_model(profile: dict[str, Any]) -> str:
    """Return profile model name."""
    return str(profile.get("model", DEFAULT_MODEL))


def get_profile_manufacturer(profile: dict[str, Any]) -> str:
    """Return profile manufacturer."""
    return str(profile.get("manufacturer", MANUFACTURER))


def get_timer_config(profile: dict[str, Any]) -> dict[str, Any]:
    """Return normalized timer settings for a profile."""
    timer = profile.get("timer", {})
    if not isinstance(timer, dict):
        timer = {}
    normalized = {
        "supported": bool(timer.get("supported", False)),
        "enable_register": _as_optional_int(timer.get("enable_register")),
        "start_hour_register": _as_optional_int(timer.get("start_hour_register")),
        "start_minute_register": _as_optional_int(timer.get("start_minute_register")),
        "stop_hour_register": _as_optional_int(timer.get("stop_hour_register")),
        "stop_minute_register": _as_optional_int(timer.get("stop_minute_register")),
        "allow_cross_midnight": bool(timer.get("allow_cross_midnight", True)),
    }
    return normalized


def _as_optional_int(value: Any) -> int | None:
    """Convert value to int or return None for invalid values."""
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None
