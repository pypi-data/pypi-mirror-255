from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    overload,
)

import attrs
from typing_extensions import Literal

from cleanchausie.consts import empty
from cleanchausie.errors import Error, ValidationError
from cleanchausie.fields.field import Field, Omittable, Required
from cleanchausie.fields.types.polymorphic import PolySchemaMapping
from cleanchausie.schema import Schema, field_def_from_annotation
from cleanchausie.schema_definition import (
    SchemaDefinition,
    clean_def,
    serialize_def,
)


def convert_attrib_to_field(attrib: attrs.Attribute) -> Field:
    """Convert attr Attribute to cleanchausie Field."""
    if attrib.type:
        field = field_def_from_annotation(attrib.type)
        assert field
    else:
        field = Field(
            validators=(),
            accepts=(),
            nullability=Required(),
            depends_on=(),
            serialize_to=None,
            serialize_func=lambda v: v,
        )

    if attrib.default is not attrs.NOTHING:
        nullability = Omittable(omitted_value=attrib.default)
        field = attrs.evolve(field, nullability=nullability)

    if attrib.validator:

        def _validate(value):
            try:
                # no ability to validate against other values on the
                # instance (since no instance exists yet), but should
                # support simple validation cases.
                assert attrib.validator  # for mypy
                attrib.validator(None, attrib, value)
                return value
            except Exception as e:
                return Error(msg=str(e))

        new_validators = (field.validators or ()) + (_validate,)
        field = attrs.evolve(field, validators=new_validators)

    return field


T = TypeVar("T", bound=attrs.AttrsInstance)
V = TypeVar("V")


@overload
def schema_def_from_attrs_class(
    attrs_class: Type,
    *,
    override_fields: Optional[Dict[str, Field]] = None,
    ignore_fields: Optional[Set[str]] = None,
    factory: Callable[..., V],
) -> SchemaDefinition[V]:
    ...


@overload
def schema_def_from_attrs_class(
    attrs_class: Type[T],
    *,
    override_fields: Optional[Dict[str, Field]] = None,
    ignore_fields: Optional[Set[str]] = None,
    factory: Literal[None] = None,
) -> SchemaDefinition[T]:
    ...


def schema_def_from_attrs_class(
    attrs_class: Any,
    *,
    override_fields: Optional[Dict[str, Field]] = None,
    ignore_fields: Optional[Set[str]] = None,
    factory: Any = None,
) -> SchemaDefinition:
    fields = override_fields.copy() if override_fields else {}
    for attr_field in attrs.fields(attrs_class):
        if ignore_fields and attr_field.name in ignore_fields:
            continue
        if attr_field.name not in fields:
            fields[attr_field.name] = convert_attrib_to_field(attr_field)

    return SchemaDefinition(
        fields=fields, factory=factory if factory is not None else attrs_class
    )


def schema_for_attrs_class(
    attrs_class: Type,
    *,
    override_fields: Optional[Dict[str, Field]] = None,
    ignore_fields: Optional[List[str]] = None,
) -> Type[Any]:
    # Note that this function actually returns a `Schema` subclass, but if
    # annotated as `Type[Schema]` then mypy will complain about the dynamically
    # defined attributes on instances of that type.
    schema_definition = schema_def_from_attrs_class(
        attrs_class=attrs_class,
        override_fields=override_fields,
        ignore_fields=set(ignore_fields or []),
    )
    return type(
        f"{attrs_class.__name__}Schema",
        (Schema,),
        schema_definition.fields,
    )


def poly_schema_mapping_for_attrs(
    t: Type[T],
    public_type: str,
    *,
    override_fields: Optional[Dict[str, Field]] = None,
    ignore_fields: Optional[Set[str]] = None,
) -> PolySchemaMapping[T]:
    schema_def = schema_def_from_attrs_class(
        t, override_fields=override_fields, ignore_fields=ignore_fields
    )

    def _serializer(instance: T) -> dict:
        return serialize_def(schema_def, attrs.asdict(instance, recurse=False))

    def _clean(data: Any, context: Any = empty) -> Union[T, ValidationError]:
        # there's some sort of mypy bug here where it gets `clean`'s generic
        # type wrong and wants `SchemaDefinition[Union[T, ValidationError]]`
        return clean_def(schema_def, data, context)  # type: ignore[arg-type]

    return PolySchemaMapping(
        public_type=public_type,
        internal_type=t,
        serializer=_serializer,
        clean=_clean,
    )
