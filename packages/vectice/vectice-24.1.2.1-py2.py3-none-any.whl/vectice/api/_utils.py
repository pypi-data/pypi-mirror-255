from __future__ import annotations

from datetime import datetime


def read_nodejs_date(date_as_string: str | None) -> datetime | None:
    if date_as_string is None:
        return None
    return datetime.strptime(date_as_string, "%Y-%m-%dT%H:%M:%S.%f%z")
