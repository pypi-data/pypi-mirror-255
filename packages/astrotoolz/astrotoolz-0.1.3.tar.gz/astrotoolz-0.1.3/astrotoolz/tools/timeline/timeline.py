from collections import defaultdict
from datetime import datetime as dt
from typing import List, Type

from astrotoolz.core.events.astro_event import AstroEvent
from astrotoolz.util.cached_property import CachedProperty


class Timeline:
    events: List[Type[AstroEvent]]

    def __init__(self, events: List[Type[AstroEvent]]):
        # self.events = sorted(events, key=lambda x: x.dt)
        self.events = events

    @CachedProperty
    def grouped_events(self) -> defaultdict[dt, List[Type[AstroEvent]]]:
        return self._group_events_by_date()

    def _group_events_by_date(self):
        grouped_events = defaultdict(list)
        for event in self.events:
            grouped_events[event.dt.date()].append(event)
        return dict(sorted(grouped_events.items()))
