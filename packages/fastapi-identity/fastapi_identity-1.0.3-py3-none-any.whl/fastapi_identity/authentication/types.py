from typing import TypedDict, NotRequired


class _FailAnnotation(TypedDict):
    failure: NotRequired[Exception]
    failure_message: NotRequired[str]