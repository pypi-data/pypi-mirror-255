"""Python method annotation parser into jsonschema validators.

It deals with magic so there's a lot of "noqa" here in the code.
"""

import abc
import enum
import inspect
import sys
from collections.abc import Collection, Iterable
from dataclasses import MISSING, fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from inspect import _ParameterKind  # noqa
from numbers import Number
from textwrap import dedent
from types import SimpleNamespace
from typing import (  # noqa
    Callable,
    Literal,
    Mapping,
    NamedTuple,
    NewType,
    Set,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    Union,
    _GenericAlias,
    _TypedDictMeta,
    cast,
)
from uuid import UUID, SafeUUID

import kaiju_tools.jsonschema as j
from kaiju_tools.registry import ClassRegistry


__all__ = ['AnnotationParser', 'FunctionAnnotation', 'TYPE_PARSERS', 'MethodSignatureError']


NoneType = type(None)


def is_generic(value) -> bool:
    """Check if an object is a generic."""
    return isinstance(value, _GenericAlias)


def get_generic_alias(obj: Type) -> Union[_GenericAlias, None]:
    return next((n for n in getattr(obj, '__orig_bases__', []) if is_generic(n)), None)


def is_typeddict(value) -> bool:
    """Check if an object is a typed dict."""
    return isinstance(value, _TypedDictMeta)


def is_namedtuple(value) -> bool:
    """Check if a value is a named tuple."""
    return inspect.isclass(value) and issubclass(value, tuple) and hasattr(value, '_fields')


def is_union_type(value) -> bool:
    """Check if an object is a union."""
    return getattr(value, '__origin__', None) is Union


class MethodSignatureError(Exception):
    """Method signature does not match the current RPC specification."""


class FunctionAnnotation(TypedDict):
    """Function annotation data."""

    title: str
    description: str
    documentation: str
    params: j.JSONSchemaObject
    returns: j.JSONSchemaObject


class AnnotationParser:
    """Parser for python annotations."""

    @classmethod
    def parse_method(cls, service_cls: Type, route: str, method: Callable, /) -> FunctionAnnotation:
        """Parse public route and method."""
        params, returns = cls.parse_function_annotations(service_cls, method)
        doc = inspect.getdoc(method)
        annotation = FunctionAnnotation(
            title=route,
            description=cls.get_function_short_description(doc),
            documentation=doc,
            params=params,
            returns=returns,
        )
        return annotation

    @classmethod
    def get_function_short_description(cls, doc: Union[str, None], /) -> Union[str, None]:
        """Extract and normalize function description (first row)."""
        if doc:
            doc = dedent(doc)
            doc = doc.split('\n')[0]
            doc.capitalize()
            return doc

    @classmethod
    def parse_function_annotations(
        cls, service_cls: Type, f: Callable
    ) -> Tuple[j.JSONSchemaObject, j.JSONSchemaObject]:
        """Parse function arguments and result into jsonschema objects."""
        sign = inspect.signature(f)
        params, required = {}, []
        additional_properties = False
        for name, arg in sign.parameters.items():
            if name.startswith('_'):
                continue
            elif name in {'self', 'cls', 'mcs'}:
                continue
            elif arg.kind == _ParameterKind.VAR_POSITIONAL:
                continue  # *args (skipped because positionals not allowed in our server)
            elif arg.kind == _ParameterKind.VAR_KEYWORD:
                additional_properties = True
                continue  # **kws (means you can pass any keys)
            elif arg.kind == _ParameterKind.POSITIONAL_ONLY:
                raise MethodSignatureError('Invalid RPC method signature: POSITIONAL ONLY arguments not allowed.')
            elif type(arg.annotation) is TypeVar:
                annotation = cls.parse_generic_alias(service_cls, arg.annotation)
            else:
                annotation = arg.annotation
            if arg.default == arg.empty:
                default = ...
                required.append(name)
            else:
                default = arg.default
            params[name] = cls.parse_annotation(annotation, default)
        if params:
            params = j.Object(properties=params, required=required, additionalProperties=additional_properties)
        else:
            params = None
        returns = cls.parse_annotation(sign.return_annotation, ..., returns_only=True)
        return params, returns

    @staticmethod
    def parse_annotation(annotation, /, default=..., returns_only: bool = False) -> j.JSONSchemaObject:
        """Convert python annotation into a jsonschema object."""
        for parser in TYPE_PARSERS.values():
            if not returns_only and parser.returns_only:
                continue
            if parser.can_parse(annotation):
                annotation = parser.parse_annotation(annotation)
                break
        else:
            if annotation == inspect._empty:  # noqa
                title = None
            else:
                title = str(annotation)
            annotation = j.JSONSchemaObject(title=title)
        if default is not ...:
            annotation.default = default
        return annotation

    @staticmethod
    def parse_generic_alias(service_cls, annotation):
        """Parse a class containing Generic hints in itself."""
        alias = base_alias = get_generic_alias(service_cls)
        args = base_args = alias.__args__
        while base_alias:
            base_args = base_alias.__args__
            base_cls = base_alias.__origin__
            base_alias = get_generic_alias(base_cls)
        try:
            annotation = args[base_args.index(annotation)]
        except (ValueError, IndexError):
            pass
        return annotation


class TypeParser(abc.ABC):
    returns_only: bool = False  # use this parser only when parsing a return value

    @classmethod
    @abc.abstractmethod
    def can_parse(cls, annotation, /) -> bool:
        ...

    @classmethod
    @abc.abstractmethod
    def parse_annotation(cls, annotation, /) -> j.JSONSchemaObject:
        ...

    @classmethod
    def get_origin(cls, annotation, /):
        return getattr(annotation, '__origin__', None)

    @classmethod
    def get_args(cls, annotation, /):
        return getattr(annotation, '__args__', None)

    @classmethod
    def is_generic(cls, annotation, /) -> bool:
        return is_generic(annotation)

    @classmethod
    def is_union_type(cls, annotation, /) -> bool:
        return is_union_type(annotation)

    @classmethod
    def parse_args(cls, args, /):
        if args:
            for arg in args:
                if arg is not ...:
                    yield AnnotationParser.parse_annotation(arg)


class SimpleTypeParser(TypeParser, abc.ABC):
    _types: Set[Type]
    _annotation_class: Type[j.JSONSchemaObject]
    _attrs: dict = None

    @classmethod
    def can_parse(cls, annotation) -> bool:
        origin = cls.get_origin(annotation)
        if origin:
            return origin in cls._types
        else:
            return annotation in cls._types

    @classmethod
    def parse_annotation(cls, annotation) -> j.JSONSchemaObject:
        _attrs = {} if cls._attrs is None else cls._attrs
        return cls._annotation_class(**_attrs)  # noqa


class StringParser(SimpleTypeParser):
    _types = {str, bytes}
    _annotation_class = j.String


class UUIDParser(SimpleTypeParser):
    _types = {UUID, SafeUUID}
    _annotation_class = j.GUID


class DateParser(SimpleTypeParser):
    _types = {date}
    _annotation_class = j.Date


class DateTimeParser(SimpleTypeParser):
    _types = {datetime}
    _annotation_class = j.DateTime


class IntegerParser(SimpleTypeParser):
    _types = {int}
    _annotation_class = j.Integer


class NumberParser(SimpleTypeParser):
    _types = {float, Decimal, Number}
    _annotation_class = j.Number


class BooleanParser(SimpleTypeParser):
    _types = {bool}
    _annotation_class = j.Boolean


class NullParser(SimpleTypeParser):
    _types = {None, NoneType}
    _annotation_class = j.Null


class TypeVarParser(TypeParser):
    @classmethod
    def can_parse(cls, annotation) -> bool:
        return isinstance(annotation, TypeVar)

    @classmethod
    def parse_annotation(cls, annotation: TypeVar) -> j.JSONSchemaObject:
        title = annotation.__name__
        annotation = annotation.__bound__
        arg = AnnotationParser.parse_annotation(annotation)
        arg.title = title
        return arg


class NewTypeParser(TypeParser):
    @classmethod
    def can_parse(cls, annotation) -> bool:
        if sys.version_info[1] < 10:
            return getattr(annotation, '__qualname__', '').split('.')[0] == 'NewType'
        else:
            return isinstance(annotation, NewType)  # noqa

    @classmethod
    def parse_annotation(cls, annotation: NewType) -> j.JSONSchemaObject:
        title = annotation.__name__
        annotation = annotation.__supertype__
        arg = AnnotationParser.parse_annotation(annotation)
        arg.title = title
        return arg


class ConstantParser(TypeParser):
    @classmethod
    def can_parse(cls, annotation) -> bool:
        return getattr(annotation, '__origin__', None) is Literal

    @classmethod
    def parse_annotation(cls, annotation) -> j.JSONSchemaObject:
        return j.Enumerated(enum=list(annotation.__args__))


class UnionParser(TypeParser):
    @classmethod
    def can_parse(cls, annotation) -> bool:
        return is_union_type(annotation)

    @classmethod
    def parse_annotation(cls, annotation) -> j.JSONSchemaObject:
        args = cls.get_args(annotation)
        return j.AnyOf(*cls.parse_args(args))


class ListParser(SimpleTypeParser):
    _types = {list, Collection, Iterable}
    _annotation_class = j.Array

    @classmethod
    def parse_annotation(cls, annotation) -> j.JSONSchemaObject:
        args = cls.get_args(annotation)
        if args is None:
            return cls._annotation_class()
        _args = []
        for arg in cls.parse_args(args):
            if type(arg) is j.AnyOf:
                arg = cast(j.AnyOf, arg)
                _args.extend(arg.items)  # noqa (ported)
            else:
                _args.append(arg)
        if len(_args) == 1:
            return cls._annotation_class(items=_args[0])
        else:
            return cls._annotation_class(items=j.AnyOf(*_args))


class SetParser(ListParser):
    _types = {set, frozenset}

    @classmethod
    def parse_annotation(cls, annotation) -> j.JSONSchemaObject:
        annotation = super().parse_annotation(annotation)
        annotation.uniqueItems = True
        return annotation


class TupleParser(ListParser):
    _types = {tuple}

    @classmethod
    def parse_annotation(cls, annotation) -> j.JSONSchemaObject:
        args = cls.get_args(annotation)
        if not args or args[1] is ...:
            return super().parse_annotation(annotation)
        return cls._annotation_class(prefixItems=list(cls.parse_args(args)))


class DictParser(SimpleTypeParser):
    _types = {dict, Mapping, SimpleNamespace}

    @classmethod
    def parse_annotation(cls, annotation) -> j.JSONSchemaObject:
        return j.Object()


class TypedDictParser(TypeParser):
    @classmethod
    def can_parse(cls, annotation) -> bool:
        return is_typeddict(annotation)

    @classmethod
    def parse_annotation(cls, annotation: TypedDict) -> j.JSONSchemaObject:
        title = annotation.__name__
        total = getattr(annotation, '__total__', True)
        properties, required = {}, []
        for key, arg in annotation.__annotations__.items():
            if total:
                required.append(key)
            # if key in annotation.__required_keys__:  # noqa pycharm
            #     required.append(key)
            # origin = cls.get_origin(arg)
            # if origin in {Required, NotRequired}:  # noqa
            #     arg = cls.get_args(arg)[0]
            arg = AnnotationParser.parse_annotation(arg)
            properties[key] = arg
        return j.Object(
            properties=properties,
            required=required,
            description=annotation.__doc__,
            additionalProperties=False,
            title=title,
        )


class NamedTupleParser(TypeParser):
    @classmethod
    def can_parse(cls, annotation) -> bool:
        return is_namedtuple(annotation)

    @classmethod
    def parse_annotation(cls, annotation: NamedTuple) -> j.JSONSchemaObject:
        title = annotation.__name__
        defaults = annotation._field_defaults  # noqa
        annotations = getattr(annotation, '__annotations__', {})  # noqa
        items = []
        for key in annotation._fields:  # noqa
            arg = AnnotationParser.parse_annotation(annotations[key]) if key in annotations else j.JSONSchemaObject()
            arg.title = key
            if key in defaults:
                arg.default = defaults[key]
            items.append(arg)
        return j.Array(prefixItems=items, description=annotation.__doc__, title=title)


class EnumValueParser(TypeParser):
    returns_only = True

    @classmethod
    def can_parse(cls, annotation) -> bool:
        return isinstance(annotation, Enum)

    @classmethod
    def parse_annotation(cls, annotation: enum.Enum) -> j.JSONSchemaObject:
        title = annotation.__class__.__name__
        return j.Constant(const=annotation.value, title=title)


class EnumTypeParser(TypeParser):
    returns_only = True

    @classmethod
    def can_parse(cls, annotation) -> bool:
        return inspect.isclass(annotation) and issubclass(annotation, Enum)

    @classmethod
    def parse_annotation(cls, annotation: Type[enum.Enum]) -> j.JSONSchemaObject:
        title = annotation.__name__
        return j.JSONSchemaObject(
            description=annotation.__doc__,
            enum=[v.value for k, v in annotation._member_map_.items()],  # noqa
            title=title,
        )


class DataclassParser(TypeParser):
    returns_only = True

    @classmethod
    def can_parse(cls, annotation) -> bool:
        return is_dataclass(annotation)

    @classmethod
    def parse_annotation(cls, annotation) -> j.JSONSchemaObject:
        title = annotation.__name__
        properties, required = {}, []
        for field in fields(annotation):
            if not field.name.startswith('_'):
                properties[field.name] = arg = AnnotationParser.parse_annotation(field.type)
                if field.default is MISSING:
                    required.append(field.name)
                else:
                    arg.default = field.default
        return j.Object(properties=properties, required=required, additionalProperties=False, title=title)


class TypeParsers(ClassRegistry[str, Type[TypeParser]]):
    """Annotation type parsers."""

    @classmethod
    def get_base_classes(cls) -> Tuple[Type, ...]:
        return (TypeParser,)


TYPE_PARSERS = TypeParsers()
TYPE_PARSERS.register_from_namespace(locals())
