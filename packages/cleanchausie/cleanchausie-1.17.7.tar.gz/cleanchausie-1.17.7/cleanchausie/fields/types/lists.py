from typing import Any, List, TypeVar, Union

from cleanchausie.consts import EMPTY, empty, omitted
from cleanchausie.errors import Error, Errors
from cleanchausie.fields.field import Field, field
from cleanchausie.fields.utils import passthrough
from cleanchausie.fields.validation import validate_field

T = TypeVar("T")


def ListField(  # noqa: N802
    inner_field: Field[T],
    *,
    min_length: Union[EMPTY, int] = empty,
    max_length: Union[EMPTY, int] = empty,
) -> Field[List[T]]:
    from cleanchausie import serialize

    @passthrough((None, omitted))
    def _call(
        value: Any, root_value, intermediate_results, context=empty
    ) -> Union[List[T], Error, Errors]:
        result = _impl(value)
        if not isinstance(result, (Error, Errors)):
            inner_results = [
                validate_field(
                    field=inner_field,
                    path=(idx,),
                    root_value=root_value,
                    value=inner_value,
                    context=context,
                    intermediate_results=intermediate_results,
                )
                for idx, inner_value in enumerate(value)
            ]
            flattened_errors = []
            for r in inner_results:
                if isinstance(r, Errors):
                    flattened_errors.extend(r.flatten())
            if flattened_errors:
                return Errors(errors=flattened_errors)
            else:
                # construct result with the validated inner data
                result = [
                    v.value for v in inner_results if not isinstance(v, Errors)
                ]
        return result

    def _impl(value: Any) -> Union[List[T], Error]:
        if isinstance(value, tuple):
            value = list(value)

        if isinstance(value, list):
            if isinstance(max_length, int) and len(value) > max_length:
                return Error(msg=f"Must be no more than {max_length} items.")

            if isinstance(min_length, int) and len(value) < min_length:
                return Error(msg=f"Must contain at least {min_length} items.")

            return value

        return Error(msg="Value is not a list")

    def serialize_func(value: List[T]) -> Any:
        return [serialize(inner_field, v) for v in value]

    return field(_call, serialize_func=serialize_func)
