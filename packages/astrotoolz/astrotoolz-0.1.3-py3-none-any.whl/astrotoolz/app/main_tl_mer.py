from astrotoolz.tools.timeline.timeline_config_parser import (
    parse_json_to_timeline_configs,
)
from astrotoolz.tools.timeline.timeline_factory import create_timelines
from astrotoolz.tools.timeline.timeline_printer import TimelinePrinter
from astrotoolz.util.common import measure

mer_sun = """
{
  "configurations": [
    {
      "coordinateSystem": "geo",
      "startDate": "2020-01-01",
      "endDate": "2025-01-01",
      "intervalMinutes": 60,
      "points": ["mercury"],
      "nodeCalc": "mean",
      "aspects": [
          {
              "angle": 360,
              "family": true,
              "orb": 0.1,
              "targets": ["sun"]
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
        printer.print_to_file("tl_mer_sun.txt")


if __name__ == "__main__":
    measure(lambda: timeline(mer_sun))
