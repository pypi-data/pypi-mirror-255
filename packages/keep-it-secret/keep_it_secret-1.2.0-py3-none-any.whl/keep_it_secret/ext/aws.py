# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import typing

import boto3

from keep_it_secret.fields import EnvField, Field
from keep_it_secret.secrets import Secrets


class PAWSSecretsManagerClient(typing.Protocol):
    def get_secret_value(self,
                         *,
                         SecretId: str,
                         VersionString: str | None = None,
                         VersionStage: str | None = None) -> typing.Any:
        ...


class AWSSecrets(Secrets):
    """
    Concrete :py:class:`keep_it_secret.Secrets` subclass that maps environment
    variables to AWS credentials.
    """

    access_key_id: str | None = EnvField.new('AWS_ACCESS_KEY_ID', required=False)
    """
    Maps ``AWS_ACCESS_KEY_ID`` environment variable. Optional, defaults to
    ``None``.

    :type: ``str | None``
    """

    secret_access_key: str | None = EnvField.new('AWS_SECRET_ACCESS_KEY', required=False)
    """
    Maps ``AWS_SECRET_ACCESS_KEY`` environment variable. Optional, defaults to
    ``None``.

    :type: ``str | None``
    """

    session_token: str | None = EnvField.new('AWS_SESSION_TOKEN', required=False)
    """
    Maps ``AWS_SESSION_TOKEN`` environment variable. Optional, defaults to
    ``None``.

    :type: ``str | None``
    """

    region_name: str | None = EnvField.new('AWS_DEFAULT_REGION', required=False)
    """
    Maps ``AWS_DEFAULT_REGION`` environment variable. Optional, defaults to
    ``None``.

    :type: ``str | None``
    """

    def __init__(self, parent: Secrets | None = None):
        super().__init__(parent=parent)

        self.client: PAWSSecretsManagerClient | None = None

    def as_boto3_client_kwargs(self) -> dict[str, typing.Any]:
        """
        Return representation of the mapped variables for use in
        ``boto3.client()`` call.
        """
        result = {}

        if self.access_key_id is not None:
            result['aws_access_key_id'] = self.access_key_id

        if self.secret_access_key is not None:
            result['aws_secret_access_key'] = self.secret_access_key

        if self.session_token is not None:
            result['aws_session_token'] = self.session_token

        if self.region_name is not None:
            result['region_name'] = self.region_name

        return result

    def get_client(self) -> PAWSSecretsManagerClient:
        if self.client is None:
            self.client = boto3.client(
                'secretsmanager',
                **self.as_boto3_client_kwargs(),
            )

        return self.client


class AWSSecretsManagerField(Field):
    """
    Concrete :py:class:`keep_it_secret.Field` subclass that uses AWS Secrets
    Manager to resolve the value.

    :param secret_id: ID of the secret to fetch.
    :param default: Default value. Defaults to ``None``.
    :param decoder: A callable to decode the fetched value. Defaults to
        :py:func:`json.loads`.
    """
    def __init__(self,
                 secret_id: str,
                 default: typing.Any = None,
                 decoder: typing.Callable = json.loads,
                 **field_options):
        field_options['as_type'] = None
        super().__init__(**field_options)
        self.secret_id = secret_id
        self.default = default
        self.decoder = decoder

    @classmethod
    def new(cls: type[AWSSecretsManagerField],  # type: ignore[override]
            secret_id: str,
            default: typing.Any = None,
            decoder: typing.Callable = json.loads,
            **field_options) -> AWSSecretsManagerField:
        return cls(secret_id, default=default, decoder=decoder, **field_options)

    def get_value(self, secrets: Secrets) -> typing.Any:
        """
        Retrieve, decode and return the secret specified by *secret_id*.

        Depends on :py:class:`AWSSecrets` to be declared in ``aws`` field on
        ``secrets`` or one of its parents.

        :raises DependencyMissing: Signal that ``secrets.aws`` field is
            missing.
        :raises RequiredValueMissing: Signal the field's value is required but
            *secret_id* is not present in the Secrets Manager.
        """
        aws_secrets: AWSSecrets = secrets.resolve_dependency(
            'aws', include_parents=True,
        )
        if aws_secrets is secrets.UNRESOLVED_DEPENDENCY:
            raise self.DependencyMissing('aws')

        client = aws_secrets.get_client()

        try:
            secret = client.get_secret_value(SecretId=self.secret_id)

            return self.decoder(secret['SecretString'])
        except client.exceptions.ResourceNotFoundException as exception:  # type: ignore[attr-defined]
            if self.required is True:
                raise self.RequiredValueMissing(self.secret_id) from exception
            else:
                return self.default
