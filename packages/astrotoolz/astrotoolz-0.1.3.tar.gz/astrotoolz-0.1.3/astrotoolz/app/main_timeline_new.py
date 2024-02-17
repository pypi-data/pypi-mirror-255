from astrotoolz.tools.timeline.timeline_config_parser import (
    parse_json_to_timeline_configs,
)
from astrotoolz.tools.timeline.timeline_factory import create_timelines
from astrotoolz.tools.timeline.timeline_printer import TimelinePrinter
from astrotoolz.util.common import measure

geo = """
{
  "configurations": [
    {
      "coordinateSystem": "geo",
      "startDate": "2024-02-01",
      "endDate": "2024-03-01",
      "intervalMinutes": 60,
      "points": ["sun", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto", "north node"],
      "nodeCalc": "mean",
      "events": [
        "TropicalSignChange",
        "TermChange",
        "DecanChange",
        "DirectionChange"
      ],
      "aspects": [
          {
              "angle": 30,
              "family": true,
              "orb": 0.1
          }
      ]
    },
    {
      "coordinateSystem": "geo",
      "startDate": "2024-02-02",
      "endDate": "2024-03-01",
      "intervalMinutes": 1,
      "points": ["moon"],
      "nodeCalc": "mean",
      "aspects": [
          {
              "angle": 30,
              "family": true,
              "orb": 0.01,
              "targets": ["sun"]
          }
      ]
    }
  ]
}
"""

moon_sun = """
{
  "configurations": [
    {
      "coordinateSystem": "geo",
      "startDate": "2024-01-01",
      "endDate": "2024-01-31",
      "intervalMinutes": 1,
      "points": ["moon"],
      "nodeCalc": "mean",
      "aspects": [
          {
              "angle": 30,
              "family": true,
              "orb": 0.01,
              "targets": ["sun"]
          }
      ]
    }
  ]
}
"""

helio = """
{
  "configurations": [
    {
      "coordinateSystem": "helio",
      "startDate": "2024-02-01",
      "endDate": "2024-03-01",
      "intervalMinutes": 60,
      "points": ["mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"],
      "nodeCalc": "mean",
      "aspects": [
          {
              "angle": 30,
              "family": true,
              "orb": 0.1
          }
      ]
    }
  ]
}
"""


def timeline(json_data: str):
    cfgs = parse_json_to_timeline_configs(json_data)

    for cfg in cfgs:
        cfg.validate()

    timelines = create_timelines(cfgs)

    for tl in timelines:
        printer = TimelinePrinter(tl)
        printer.print_to_file("timeline_feb_helio.txt")


if __name__ == "__main__":
    measure(lambda: timeline(helio))
