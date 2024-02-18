# -*- coding: utf-8 -*-
from __future__ import annotations

import typing

import hvac

from keep_it_secret.fields import EnvField, Field
from keep_it_secret.secrets import Secrets


class VaultSecrets(Secrets):
    """
    Concrete :py:class:`keep_it_secret.Secrets` subclass that maps environment
    variables to Vault credentials.
    """

    url: str = EnvField.new('VAULT_URL', required=True)
    """
    Maps ``VAULT_URL`` environment variable.

    :type: ``str``
    """

    token: str = EnvField.new('VAULT_TOKEN', required=True)
    """
    Maps ``VAULT_TOKEN`` environment variable.

    :type: ``str``
    """

    client_cert_path: str | None = EnvField.new('VAULT_CLIENT_CERT_PATH', required=False)
    """
    Maps ``VAULT_CLIENT_CERT_PATH`` environment variable.

    :type: ``str | None``
    """

    client_key_path: str | None = EnvField.new('VAULT_CLIENT_KEY_PATH', required=False)
    """
    Maps ``VAULT_CLIENT_KEY_PATH`` environment variable.

    :type: ``str | None``
    """

    server_cert_path: str | None = EnvField.new('VAULT_SERVER_CERT_PATH', required=False)
    """
    Maps ``VAULT_SERVER_CERT_PATH`` environment variable.

    :type: ``str | None``
    """

    def __init__(self, parent: Secrets | None = None):
        super().__init__(parent)

        self.client: hvac.Client | None = None

    def as_hvac_client_kwargs(self) -> dict[str, typing.Any]:
        """
        Return representation of the mapped variables for use in
        ``hvac.Client`` constructor.
        """
        result: dict[str, typing.Any] = {
            'url': self.url,
            'token': self.token,
        }

        if self.client_cert_path is not None and self.client_key_path is not None:
            result['cert'] = (self.client_cert_path, self.client_key_path)

        if self.server_cert_path is not None:
            result['verify'] = self.server_cert_path

        return result

    def get_client(self) -> hvac.Client:
        """
        Return the ``hvac.Client`` instance configured using the credentials.
        """
        if self.client is None:
            self.client = hvac.Client(
                **self.as_hvac_client_kwargs(),
            )

        return self.client


class VaultKV2Field(Field):
    """
    Concrete :py:class:`keep_it_secret.Field` subclass that uses Hashicorp
    Vault KV V2 secrets engine to resolve the value.

    If ``as_type`` isn't provided, the fetched value will be returned as-is (
    i.e. as a dict). Otherwise, ``as_type`` should be a type which accepts
    kwargs representing the value's keys in its constructor.

    :param mount_point: Mount path for the secret engine.
    :param path: Path to the secret to fetch.
    :param version: Version identifier. Defaults to ``None`` (aka the newest
        version).
    :param default: Default value. Defaults to ``None``.
    """

    def __init__(self,
                 mount_point: str,
                 path: str,
                 version: str | None = None,
                 default: typing.Any = None,
                 **field_options):
        super().__init__(**field_options)

        as_type: type | None = field_options.pop('as_type', None)
        self.as_type = self.cast if as_type is not None else None  # type: ignore[assignment]

        self.mount_point = mount_point
        self.path = path
        self.version = version
        self.default = default
        self.cast_to = as_type

    @classmethod
    def new(cls: type[VaultKV2Field],  # type: ignore[override]
            mount_point: str,
            path: str,
            version: str | None = None,
            default: typing.Any = None,
            **field_options):
        return cls(mount_point, path, version=version, default=default, **field_options)

    def cast(self, data: typing.Any) -> typing.Any:
        """
        Cast ``data`` to the type specified in ``as_type`` argument of the
        constructor.
        """
        if isinstance(data, dict) is False:
            return data

        if self.cast_to is None:
            return data

        return self.cast_to(**data)

    def get_value(self, secrets: Secrets) -> typing.Any:
        """
        Retrieve, decode and return the secret stored in a KV V2 secrets engine
        mounted at *mount_path* under the path *path*.

        Depends on :py:class:`VaultSecrets` to be declared in ``vault`` field
        on ``secrets`` or one of its parents.

        :raises DependencyMissing: Signal that ``secrets.aws`` field is
            missing.
        :raises RequiredValueMissing: Signal the field's value is required but
            *secret_id* is not present in the secrets engine.
        """
        vault_secrets: VaultSecrets = secrets.resolve_dependency(
            'vault', include_parents=True,
        )
        if vault_secrets is secrets.UNRESOLVED_DEPENDENCY:
            raise self.DependencyMissing('vault')

        client = vault_secrets.get_client()

        try:
            secret_response = client.secrets.kv.v2.read_secret_version(
                self.path,
                version=self.version,
                mount_point=self.mount_point,
                raise_on_deleted_version=True,
            )

            return secret_response['data']['data']
        except hvac.exceptions.InvalidPath as exception:
            if self.required is True:
                raise self.RequiredValueMissing(f'{self.mount_point}{self.path}') from exception
            else:
                return self.default
