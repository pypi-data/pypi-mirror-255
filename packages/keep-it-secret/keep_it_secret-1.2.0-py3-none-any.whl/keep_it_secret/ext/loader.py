# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib
import typing


def load_secrets(package: str, env: str, app: str) -> typing.Any:
    """
    A basic secrets loader. Will attempt to import the secrets module and
    return the ``__secrets__`` attribute.

    :param package: The package which contains the module.
    :param env: Environment identifier (e.g. ``development``).
    :param app: Application identifier (e.g. ``weather_service``).
    """
    secrets_module = importlib.import_module(f'{package}.{env}.{app}')
    return secrets_module.__secrets__
