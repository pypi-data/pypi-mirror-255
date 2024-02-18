import contextlib
import datetime
import functools
import typing
from typing import Dict, Type, TypeVar

from cleanchausie.fields.field import Field
from cleanchausie.fields.types.tzinfo import TimezoneField


def _get_field_type_map() -> Dict[Type, Field]:
    from .types.bools import BoolField
    from .types.datetimes import DateTimeField, TimeDeltaField, TimeField
    from .types.numbers import FloatField, IntField
    from .types.strings import StrField

    return {
        int: IntField(),
        float: FloatField(),
        str: StrField(),
        bool: BoolField(),
        datetime.time: TimeField(),
        datetime.datetime: DateTimeField(),
        datetime.timedelta: TimeDeltaField(),
        datetime.tzinfo: TimezoneField(),
    }


def get_extra_field_types():
    # try to automatically support pytz fields if it's installed
    with contextlib.suppress(ImportError):
        from pytz import BaseTzInfo

        from cleanchausie.ext.pytz import PytzTimezoneField

        yield BaseTzInfo, PytzTimezoneField()


FMapType = TypeVar("FMapType")


@functools.lru_cache
def get_field_for_basic_type(basic_type: Type[FMapType]) -> Field[FMapType]:
    from .types.any import AnyField

    with contextlib.suppress(KeyError):
        return _get_field_type_map()[basic_type]
    for extra_type, extra_field in get_extra_field_types():
        if basic_type == extra_type:
            return extra_field
    if basic_type is typing.Any:
        return AnyField()
    raise TypeError
