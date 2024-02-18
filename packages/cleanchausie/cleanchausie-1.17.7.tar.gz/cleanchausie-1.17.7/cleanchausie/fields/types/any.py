from typing import Any

from cleanchausie.fields.field import Field, Required, field
from cleanchausie.fields.utils import noop


def AnyField() -> Field[Any]:  # noqa: N802
    """
    Anything you put into it comes out unaffected.

    It allows Nones by default too.
    """
    return field(noop, nullability=Required(allow_none=True))
