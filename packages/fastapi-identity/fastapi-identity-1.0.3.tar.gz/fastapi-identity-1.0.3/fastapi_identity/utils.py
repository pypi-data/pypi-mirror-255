import dataclasses
import inspect
import uuid
from datetime import datetime, UTC, timedelta
from sys import platform
from typing import Optional


def asdict(data, exclude_none=True):
    if exclude_none:
        return dataclasses.asdict(data, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
    else:
        return dataclasses.asdict


def timespan(
        days=0,
        seconds=0,
        microseconds=0,
        milliseconds=0,
        minutes=0,
        hours=0,
        weeks=0,
        *,
        td: timedelta = None
):
    if td is not None:
        return datetime.now(UTC) + td

    return datetime.now(UTC) + timedelta(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        milliseconds=milliseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks
    )


def isnull(s: Optional[str]) -> bool:
    return s is None or not s or s.isspace()


def funcname():
    return inspect.stack()[1][3]


def get_device_uuid():
    return uuid.UUID(int=uuid.getnode())
