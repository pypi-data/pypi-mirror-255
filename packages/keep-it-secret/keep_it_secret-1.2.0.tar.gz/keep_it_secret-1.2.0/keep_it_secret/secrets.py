# -*- coding: utf-8 -*-
from __future__ import annotations

import typing

from keep_it_secret.fields import Field

TFields: typing.TypeAlias = dict[str, Field]


def process_class_attributes(attributes) -> tuple[dict[str, typing.Any], TFields]:
    new_attributes: dict[str, typing.Any] = {}
    fields: TFields = {}

    for attribute_name, attribute in attributes.items():
        if isinstance(attribute, Field) is True:
            fields[attribute_name] = attribute
        else:
            new_attributes[attribute_name] = attribute

    return new_attributes, fields


def field_property_factory(field_name: str, field: Field) -> property:
    def getter(instance: Secrets) -> typing.Any:
        if field_name not in instance.__secrets_data__:
            field: Field = instance.__secrets_fields__[field_name]
            instance.__secrets_data__[field_name] = field(instance)

        return instance.__secrets_data__[field_name]

    return property(fget=getter, doc=field.description)


class SecretsBase(type):
    def __new__(cls, name, bases, attributes, **kwargs):
        super_new = super().__new__

        fields = {}
        for base in bases:
            if isinstance(base, SecretsBase) is True:
                fields.update(base.__secrets_fields__)

        new_attributes, cls_fields = process_class_attributes(attributes)

        final_fields = {**fields, **cls_fields}
        new_attributes['__secrets_fields__'] = final_fields

        new_class = super_new(cls, name, bases, new_attributes, **kwargs)

        for field_name, field in final_fields.items():
            field.name = f'{name}.{field_name}'

            setattr(
                new_class,
                field_name,
                field_property_factory(field_name, field),
            )

        return new_class


class Secrets(metaclass=SecretsBase):
    """
    The base Secrets class, used to declare application-specfic secrets
    containers.

    Example:

    .. code-block:: python

        class AppSecrets(Secrets):
            secret_key: str = AbstractField.new()
            db_password: str = EnvField.new('APP_DB_PASSWORD', required=True)

            not_a_secret = 'spam'

            def do_something(self) -> bool:
                return 'eggs'

    When instantiated, ``AppSecrets`` will evaluate each of the fields and fill
    in instance properties with the appropriate values. Attributes which don't
    evaluate to :py:class:`Field` instances will not be modified.

    Secrets classes retain their behaviour when they're subclassed. This allows
    the developer to compose env-specific secrets:

    .. code-block:: python

        class DevelopmentSecrets(AppSecrets):
            secret_key: str = LiteralField.new('thisisntsecure')

    In this case, the ``secret_key`` field gets overloaded, while all the
    others remain as declared in ``AppSecrets``.

    :param parent: The parent :py:class:`Secrets` subclass or ``None``.
    """

    #: Sentinel for unresolved dependency.
    UNRESOLVED_DEPENDENCY: list[typing.Any] = []

    __secrets_fields__: TFields

    def __init__(self, parent: Secrets | None = None):
        self.__secrets_parent__ = parent

        self.__secrets_data__: dict[str, typing.Any] = {}

        for field_name, field in self.__secrets_fields__.items():
            self.__secrets_data__[field_name] = getattr(self, field_name)

    def resolve_dependency(self,
                           name: str,
                           *,
                           include_parents: bool = True) -> typing.Any:
        """
        Resolve a dependency field identified by *name* and return its value.
        returns :py:attr:`keep_it_secret.Secrets.UNRESOLVED_DEPENDENCY` if
        the value can't be resolved.

        :param include_parents: Recursively include parents, if any.
        """
        if name in self.__secrets_fields__:
            return getattr(self, name)

        if include_parents is True and self.__secrets_parent__ is not None:
            return self.__secrets_parent__.resolve_dependency(
                name, include_parents=include_parents,
            )

        return self.UNRESOLVED_DEPENDENCY
