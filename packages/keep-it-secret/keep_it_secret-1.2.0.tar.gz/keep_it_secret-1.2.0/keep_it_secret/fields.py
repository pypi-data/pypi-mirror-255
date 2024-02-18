# -*- coding: utf-8 -*-
from __future__ import annotations

import abc
import os
import typing

if typing.TYPE_CHECKING:
    from keep_it_secret.secrets import Secrets


class Field(abc.ABC):
    """
    Base class for fields.

    Example:

    .. code-block:: python

        class SpamField(Field):
            def get_value(self, secrets):
                return 'spam'

        class AppSecrets(Secrets):
            spam: str = SpamField.new()

    Normal instantiation and using the ``new()`` factory method are
    functionally equal. The ``new()`` method is provided for compatibility
    with type annotations.

    .. code-block:: pycon

        >>> spam_one = SpamField.new()
        >>> spam_two = SpamField()
        >>> spam_one(secrets) == spam_two(secrets)
        True

    The field is evaluated when its instance is called. This is done during
    initialization of the :py:class:`keep_it_secret.Secrets` subclass in which
    the field was used. The result of this is either the value cast to
    ``as_type`` (if specified) or ``None``.

    Note that the base class doesn't enforce the ``required`` flag. Its
    behaviour is implementation specific.

    :param as_type: Type to cast the value to. If ``None``, no casting will be
        done. Defaults to ``str``.
    :param required: Required flag. Defaults to ``True``.
    :param description: Human readable description. Defaults to ``None``.
    """

    class KeepItSecretFieldError(Exception):
        """Base class for field exceptions."""
        pass

    class RequiredValueMissing(KeepItSecretFieldError):
        """Raised when the field's value is required but missing."""
        pass

    class DependencyMissing(KeepItSecretFieldError):
        """Raised when the field depends on another, which isn't defined."""
        pass

    def __init__(self, *, as_type: type | None = str, required: bool = True, description: str | None = None):
        self.as_type = as_type
        self.required = required
        self.description = description
        self.name = str(self)

    @classmethod
    def new(cls: type[Field], **field_options) -> typing.Any:
        """
        The field factory. Constructs the field in a manner which is compatible
        with type annotations.

        Positional arguments, keyword arguments and *field_options* are passed
        to the constructor.
        """
        return cls(**field_options)

    def __call__(self, secrets: Secrets) -> typing.Any:
        """Evaluate the field and return the value."""
        value = self.get_value(secrets)

        if value is None:
            return None

        if self.as_type is not None:
            return self.as_type(value)

        return value

    @abc.abstractmethod
    def get_value(self, secrets: Secrets) -> typing.Any:
        """
        Get and return the field's value. Subclasses must implement this
        method.
        """
        ...


class LiteralField(Field):
    """
    Concrete :py:class:`keep_it_secret.Field` subclass that wraps a literal
    value.

    Example:

    .. code-block:: pycon

        >>> spam = LiteralField('spam')
        >>> spam(secrets)
        'spam'
        >>> one = LiteralField(1)
        >>> one()
        >>> one(secrets)
        1
        >>> anything_works = LiteralField(RuntimeError('BOOM'))
        >>> anything_works(secrets)
        RuntimeError('BOOM')

    :param value: The value to wrap.
    """

    def __init__(self, value: typing.Any, **field_options):
        field_options['as_type'] = None
        super().__init__(**field_options)

        self.value = value

    @classmethod
    def new(cls: type[LiteralField], value: typing.Any, **field_options) -> typing.Any:  # type: ignore[override]
        return cls(value, **field_options)

    def get_value(self, secrets: Secrets) -> typing.Any:
        """Returns the wrapped value."""
        return self.value


class EnvField(Field):
    """
    Concrete :py:class:`keep_it_secret.Field` subclass that uses ``os.environ``
    to resolve the value.

    Example:

    .. code-block:: pycon

        >>> db_password = EnvField('APP_DB_PASSWORD')
        >>> db_password(secrets)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "/Users/bilbo/Projects/PLAYG/keep_it_secret/keep_it_secret/fields.py", line 83, in __call__
            if value is None:
          File "/Users/bilbo/Projects/PLAYG/keep_it_secret/keep_it_secret/fields.py", line 129, in get_value
            def new(cls: type[EnvField], key: str, default: typing.Any = None, **field_options) -> typing.Any:
        keep_it_secret.fields.Field.RequiredValueMissing: APP_DB_PASSWORD
        >>> os.environ['APP_DB_PASSWORD'] = 'spam'
        >>> db_password(secrets)
        'spam'

    :param key: Environment dictionary key.
    :param default: Default value. Defaults to ``None``.
    """
    def __init__(self, key: str, default: typing.Any = None, **field_options):
        super().__init__(**field_options)
        self.key = key
        self.default = default

    @classmethod
    def new(cls: type[EnvField],  # type: ignore[override]
            key: str,
            default: typing.Any = None,
            **field_options) -> typing.Any:
        return cls(key, default=default, **field_options)

    def get_value(self, secrets: Secrets) -> typing.Any:
        """
        Resolve the value using ``os.environ``.

        :raises RequiredValueMissing: Signal the field's value is required but
            *key* is not present in the environment.
        """
        if self.required is True and self.key not in os.environ:
            raise self.RequiredValueMissing(self.key)

        return os.environ.get(self.key, self.default)


class SecretsField(Field):
    """
    Concrete :py:class:`keep_it_secret.Field` subclass that wraps a
    :py:class:`keep_it_secret.Secrets` subclass. Provides API to declare
    complex secret structures.

    Example:

    .. code-block:: python

        class WeatherAPICredentials(Secrets):
            username: str = LiteralField('spam')
            password: str = EnvField.new('APP_WEATHER_API_PASSWORD', required=True)

        class AppSecrets(Secrets):
            db_password: str = EnvField.new('APP_DB_PASSWORD', required=True)
            weather_api: WeatherAPICredentials = SecretsField(WeatherAPICredentials)

    .. code-block:: pycon

        >>> secrets = AppSecrets()
        >>> secrets.weather_api.password
        'eggs'
        >>> secrets.weather_api.__secrets_parent__ == secrets
        True

    :param klass: :py:class:`keep_it_secret.Secrets` subclass to wrap.
    """
    def __init__(self, klass: type[Secrets], **field_options):
        field_options['as_type'] = None
        super().__init__(**field_options)

        self.klass = klass

    @classmethod
    def new(cls: type[SecretsField], klass: type[Secrets], **field_options) -> typing.Any:  # type: ignore[override]
        return cls(klass, **field_options)

    def get_value(self, secrets: Secrets) -> typing.Any:
        """
        Instantiate the wrapped *klass* and return it. *secrets* will be
        passed as ``parent`` to the instance.
        """
        return self.klass(parent=secrets)


class AbstractField(Field):
    """
    The "placeholder" field. Use it in a :py:class:`keep_it_secret.Secrets`
    subclass to indicate that the field must be overloaded by a subclass.

    Instances will raise :py:exc:`NotImplementedError` during evaluation.

    Example:

    .. code-block:: python

        class BaseSecrets(Secrets):
            secret_key: str = AbstractField.new()

        class DevelopmentSecrets(BaseSecrets):
            secret_key: str = LiteralField.new('thisisntsecure')

        class ProductionSecrets(BaseSecrets):
            secret_key: str = EnvField.new('APP_SECRET_KEY', required=True)

    Trying to instantiate ``BaseSecrets`` will fail:

    .. code-block:: pycon

        >>> secrets = BaseSecrets()
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "/Users/bilbo/Projects/PLAYG/keep_it_secret/keep_it_secret/secrets.py", line 105, in __init__
            self.__secrets_data__[field_name] = getattr(self, field_name)
          File "/Users/bilbo/Projects/PLAYG/keep_it_secret/keep_it_secret/secrets.py", line 27, in getter
            instance.__secrets_data__[field_name] = field(instance)
          File "/Users/bilbo/Projects/PLAYG/keep_it_secret/keep_it_secret/fields.py", line 83, in __call__
            value = self.get_value(secrets)
          File "/Users/bilbo/Projects/PLAYG/keep_it_secret/keep_it_secret/fields.py", line 171, in get_value
            raise NotImplementedError('Abstract field must be overloaded: `%s`' % self.name)
        NotImplementedError: Abstract field must be overloaded: `BaseSecrets.secret_key`

    Instantiating ``DevelopmentSecrets`` will work as expected:

    .. code-block:: pycon

        >>> secrets = DevelopmentSecrets()
        >>> secrets.secret_key
        'thisisntsecure'
    """

    def get_value(self, secrets: Secrets) -> typing.Any:
        """
        :raises NotImplementedError: Signal that the field needs to be
            overloaded.
        """
        raise NotImplementedError('Abstract field must be overloaded: `%s`' % self.name)
