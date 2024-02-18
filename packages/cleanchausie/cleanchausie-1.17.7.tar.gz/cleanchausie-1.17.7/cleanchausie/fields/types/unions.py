from typing import Any, Generic, Tuple, Type, TypeVar, Union

import attrs

from cleanchausie.consts import empty, omitted
from cleanchausie.errors import Error, Errors, ValidationError
from cleanchausie.fields.field import Field, field
from cleanchausie.fields.utils import passthrough

T = TypeVar("T", contravariant=True)


@attrs.frozen
class UnionOf(Generic[T]):
    field: Field[T]
    type_: Union[Type[T]]


def UnionField(of: Tuple[UnionOf, ...]) -> Field[Any]:  # noqa: N802
    from cleanchausie import clean, serialize

    @passthrough((None, omitted))
    def _clean(value: Any, context: Any = empty) -> Union[T, Error, Errors]:
        for of_option in of:
            if not isinstance(value, of_option.type_):
                continue

            result = clean(of_option.field, value, context=context)
            if isinstance(result, ValidationError):
                return Errors(errors=result.errors)
            else:
                return result

        # None of those matched the type already, now we have to try to clean
        # them all and see if one works without erroring
        for of_option in of:
            result = clean(of_option.field, value, context=context)
            if not isinstance(result, ValidationError):
                return result

        return Error(
            "Expected one of the following types: {}".format(
                ", ".join(of_opt.type_.__name__ for of_opt in of)
            )
        )

    @passthrough((None, omitted))
    def _serialize(value: Any) -> Any:
        for union_of in of:
            if not isinstance(value, union_of.type_):
                continue
            return serialize(union_of.field, value)

        raise ValueError("No matching type found")

    return field(_clean, serialize_func=_serialize)
