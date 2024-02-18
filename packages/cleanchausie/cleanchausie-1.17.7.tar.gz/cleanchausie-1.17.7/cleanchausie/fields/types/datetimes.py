import datetime
from typing import Any, Optional, Union

from dateutil import parser

from cleanchausie.consts import omitted
from cleanchausie.errors import Error
from cleanchausie.fields.field import Field, field
from cleanchausie.fields.utils import passthrough


def TimeField() -> Field[datetime.time]:  # noqa: N802
    def _serialize(value: Optional[datetime.time]) -> Optional[str]:
        if not isinstance(value, datetime.time):
            return value
        return value.isoformat()

    @field(serialize_func=_serialize)
    @passthrough((None, omitted))
    def _time_field(value: Any) -> Union[Error, datetime.time]:
        if isinstance(value, datetime.time):
            return value
        elif isinstance(value, str):
            try:
                return datetime.time.fromisoformat(value)
            except ValueError:
                return Error(msg=f"Could not parse time from '{value}'.")

        return Error(msg=f"Could not resolve time from type '{type(value)}'")

    return _time_field


def TimeDeltaField() -> Field[datetime.timedelta]:  # noqa: N802
    @field
    @passthrough((None, omitted))
    def _timedelta_field(value: Any) -> Union[datetime.timedelta, Error]:
        # value is either already a timedelta or is an int in seconds
        if isinstance(value, datetime.timedelta):
            return value
        elif isinstance(value, int):
            return datetime.timedelta(seconds=value)

        return Error(
            msg=f"Could not resolve timedelta from type '{type(value)}'"
        )

    return _timedelta_field


def DateTimeField() -> Field[datetime.datetime]:  # noqa: N802
    def _serialize(value: Optional[datetime.datetime]) -> Optional[str]:
        if not isinstance(value, datetime.datetime):
            return value
        return value.isoformat()

    @field(serialize_func=_serialize)
    @passthrough((None, omitted))
    def _datetimefield(value: Any) -> Union[Error, datetime.datetime]:
        if isinstance(value, datetime.datetime):
            return value
        elif isinstance(value, str):
            try:
                # TODO should we use ciso8601 to parse? It's a bit stricter, but much faster.
                return parser.parse(value)
            except ValueError:
                return Error(msg=f"Could not parse datetime from '{value}'.")
        else:
            return Error(
                msg=f"Could not resolve datetime from type '{type(value)}'"
            )

    return _datetimefield
