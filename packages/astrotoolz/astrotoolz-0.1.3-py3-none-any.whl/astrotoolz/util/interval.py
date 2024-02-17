from datetime import datetime, timedelta
from typing import List


def calculate_intervals(start_time: datetime, end_time: datetime, interval_minutes: int) -> List[datetime]:
    intervals = []
    current_time = start_time
    
    if (start_time == end_time):
        intervals.append(start_time)
        return intervals

    while current_time < end_time:
        intervals.append(current_time)
        current_time += timedelta(minutes=interval_minutes)

    return intervals

