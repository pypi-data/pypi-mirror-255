from datetime import datetime, timedelta


def get_next_datetime(now: datetime, interval: timedelta) -> datetime:
    now_in_seconds = (now - datetime.min).total_seconds()
    interval_in_seconds = interval.total_seconds()

    quotient = (now_in_seconds // interval_in_seconds) + 1

    return datetime.min + timedelta(seconds=quotient * interval_in_seconds)
