import datetime
from typing import Union

from cleanchausie.consts import OMITTED, omitted
from cleanchausie.errors import Error
from cleanchausie.fields.field import Field, field
from cleanchausie.fields.utils import passthrough

try:
    import zoneinfo
except ModuleNotFoundError:
    from backports import zoneinfo  # type: ignore[no-redef]


def TimezoneField() -> Field[datetime.tzinfo]:  # noqa: N802
    def _serialize_fn(
        value: Union[datetime.tzinfo, OMITTED, None],
    ) -> Union[str, OMITTED, None]:
        if not isinstance(value, datetime.tzinfo):
            return value
        return str(value)

    @field(serialize_func=_serialize_fn)
    @passthrough((None, omitted))
    def _timezone_field(value: str) -> Union[datetime.tzinfo, Error]:
        try:
            return zoneinfo.ZoneInfo(value)
        except (ValueError, zoneinfo.ZoneInfoNotFoundError):
            return Error(msg=f"Unknown timezone: {value}")

    return _timezone_field
