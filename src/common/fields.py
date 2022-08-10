from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional, Tuple, Type, TypeVar, Union

import six
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH, Field
from django.utils.module_loading import import_string

from .forms import EnumChoiceField


class CastOnAssignDescriptor(object):
    """
    A property descriptor which ensures that `field.to_python()` is called on _every_ assignment to the field.

    This used to be provided by the `django.db.models.subclassing.Creator` class, which in turn
    was used by the deprecated-in-Django-1.10 `SubfieldBase` class, hence the reimplementation here.
    """

    def __init__(self, field: Field) -> None:  # type: ignore[type-arg]
        self.field = field

    def __get__(self, obj: Any, type: Optional[Type[Any]] = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__[self.field.name]

    def __set__(self, obj: Any, value: Any) -> None:
        obj.__dict__[self.field.name] = self.field.to_python(value)


E = TypeVar('E', bound=Enum)


class EnumFieldMixin(models.Field):  # type: ignore[type-arg]
    def __init__(self, enum: Union[Type[E], str], **options: Any) -> None:
        if isinstance(enum, six.string_types):
            enum_cls: Type[E] = import_string(enum)
        else:
            enum_cls = enum  # type: ignore[assignment]
        self.enum = enum_cls

        if "choices" not in options:
            options["choices"] = [  # choices for the TypedChoiceField
                (i, getattr(i, 'label', i.name)) for i in self.enum
            ]

        super(EnumFieldMixin, self).__init__(**options)

    def contribute_to_class(self, cls: Type[Any], name: str) -> None:  # type: ignore[override]
        super(EnumFieldMixin, self).contribute_to_class(cls, name)
        setattr(cls, name, CastOnAssignDescriptor(self))

    def to_python(self, value: Any) -> Optional[E]:
        if value is None or value == '':
            return None
        if isinstance(value, self.enum):
            return value
        for m in self.enum:
            if value == m:
                return m
            if value == m.value or str(value) == str(m.value) or str(value) == str(m):
                return m
        raise ValidationError('%s is not a valid value for enum %s' % (value, self.enum), code="invalid_enum_value")

    def get_prep_value(self, value: E) -> Any:
        if value is None:
            return None
        if isinstance(value, self.enum):  # Already the correct type -- fast path
            return value.value
        return self.enum(value).value

    def from_db_value(self, value: E, expression: Any, connection: Any, *args: Any) -> Any:
        return self.to_python(value)

    def value_to_string(self, obj: E) -> str:  # type: ignore[override]
        """
        This method is needed to support proper serialization. While its name is value_to_string()
        the real meaning of the method is to convert the value to some serializable format.
        Since most of the enum values are strings or integers we WILL NOT convert it to string
        to enable integers to be serialized natively.
        """
        value = self.value_from_object(obj)  # type: ignore[arg-type]
        return value.value if value else None

    def get_default(self) -> Any:
        if self.has_default():
            if self.default is None:
                return None

            if isinstance(self.default, Enum):
                return self.default

            return self.enum(self.default)

        return super(EnumFieldMixin, self).get_default()

    def deconstruct(self) -> Tuple[str, str, Any, Any]:
        name, path, args, kwargs = super(EnumFieldMixin, self).deconstruct()
        kwargs['enum'] = self.enum
        kwargs.pop('choices', None)
        if 'default' in kwargs:
            if hasattr(kwargs["default"], "value"):
                kwargs["default"] = kwargs["default"].value

        return name, path, args, kwargs

    def get_choices(  # type: ignore[override]
        self, include_blank: bool = True, blank_choice: List[Tuple[str, str]] = BLANK_CHOICE_DASH
    ) -> List[Any]:
        # Force enum fields' options to use the `value` of the enumeration
        # member as the `value` of SelectFields and similar.
        return [
            (i.value if isinstance(i, Enum) else i, display)
            for (i, display) in super(EnumFieldMixin, self).get_choices(
                include_blank, blank_choice  # type: ignore[arg-type]
            )
        ]

    def formfield(
        self,
        form_class: Optional[Type[Any]] = None,
        choices_form_class: Optional[Type[Any]] = None,
        **kwargs: Any,
    ) -> Any:
        if not choices_form_class:
            choices_form_class = EnumChoiceField

        return super(EnumFieldMixin, self).formfield(
            form_class=form_class, choices_form_class=choices_form_class, **kwargs
        )


class EnumField(EnumFieldMixin, models.TextField):  # type: ignore[type-arg]
    def __init__(self, enum: Type[E], **kwargs: Any) -> None:
        if 'max_length' in kwargs:
            raise Exception('do not set "max_length" on EnumField')

        super(EnumField, self).__init__(enum, **kwargs)
        self.validators = []  # type: ignore[misc]
