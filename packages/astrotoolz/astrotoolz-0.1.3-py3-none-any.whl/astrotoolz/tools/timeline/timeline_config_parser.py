import json
from datetime import datetime
from typing import Any, Dict, List

import humps

from astrotoolz.core.enums import CoordinateSystem, NodeCalc
from astrotoolz.tools.timeline.timeline_config import AspectsConfig, TimelineConfig


def parse_json_to_timeline_configs(json_str: str) -> List[TimelineConfig]:
    try:
        data = json.loads(json_str)
        snake_case_data = humps.decamelize(data)
        return [
            _parse_single_config(config) for config in snake_case_data["configurations"]
        ]
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON: {e}")
    except KeyError as e:
        raise ValueError(f"Missing required configuration field: {e}")
    except ValueError as e:
        raise ValueError(f"Invalid configuration value: {e}")


def _parse_single_config(config: Dict[str, Any]) -> TimelineConfig:
    config["start_date"] = _parse_utc_date(config["start_date"])
    config["end_date"] = _parse_utc_date(config["end_date"])
    config["coordinate_system"] = CoordinateSystem.from_string(
        config["coordinate_system"]
    )
    config["node_calc"] = NodeCalc.from_string(config["node_calc"])
    config["events"] = _parse_events(config.get("events", []))
    config["aspects"] = _parse_aspects(config.get("aspects", []))
    return TimelineConfig(**config)


def _parse_utc_date(date_str: str) -> datetime:
    try:
        if "T" not in date_str:
            date_str += "T00:00:00Z"
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError(f"Invalid date format: {e}")


def _parse_events(events: List[str]) -> List[Any]:
    if not events:
        return []
    event_classes = [globals().get(event) for event in events]
    if None in event_classes:
        missing_events = [
            event for event, cls in zip(events, event_classes) if cls is None
        ]
        raise ValueError(f"Unknown events: {', '.join(missing_events)}")
    return event_classes


def _parse_aspects(aspects: List[Dict[str, Any]]) -> List[AspectsConfig]:
    return [AspectsConfig(**aspect) for aspect in aspects] if aspects else []
