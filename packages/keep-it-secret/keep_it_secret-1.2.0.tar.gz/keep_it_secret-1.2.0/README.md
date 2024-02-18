# Keep It Secret by BTHLabs

*Keep It Secret* is a small Python library for declarative management
of app secrets.

[Docs](https://projects.bthlabs.pl/keep-it-secret/) | [Source repository](https://git.bthlabs.pl/tomekwojcik/keep-it-secret/)

## Installation

```
$ pip install keep_it_secret
```

## Usage

*Keep It Secret* gives a developer API needed to declare secrets used
by the app and access them in a secure, uniform manner.

Consider the following example:

```
from secrets_manager import (
    AbstractField, EnvField, LiteralField, Secrets, SecretsField,
)
from secrets_manager.ext.aws import AWSSecrets, AWSSecretsManagerField

class AppSecrets(Secrets):
    secret_key: str = AbstractField.new()
    db_password: str = EnvField.new('APP_DB_PASSWORD', required=True)
    pbkdf2_iterations_count: int = EnvField(
        'APP_PBKDF2_ITERATIONS_COUNT',
        default=16384,
        required=False,
        as_type=int,
    )

class DevelopmentSecrets(AppSecrets):
    secret_key: str = LiteralField.new('thisisntsecure')

class ProductionSecrets(AppSecrets):
    aws: AWSSecrets = SecretsField.new(AWSSecrets)
    secret_key: str = AWSSecretsManagerField(
        'app/production/secret_key', required=True,
    )
    db_password: str = AWSSecretsManagerField(
        'app/production/db_password', required=True,
    )
```

The `AppSecrets` class serves as base class for environment specific classes.
The environment specific classes can overload any field, add new fields and
extend the base class to provide custom behaviour.

The `DevelopmentSecrets` class uses environment variables and literal values
to provide secrets suitable for the development environment:

```
>>> development_secrets = DevelopmentSecrets()
>>> development_secrets.secret_key
'thisisntsecure'
>>> development_secrets.db_password
'spam'
>>> development_secrets.pbkdf2_iterations_count
1024
```

The `ProductionSecrets` class uses environment variables and AWS Secrets
Manager to provide secrets suitable for the development environment:

```
>>> production_secrets = ProductionSecrets()
>>> production_secrets.aws.access_key_id
'anawsaccesskey'
>>> production_secrets.secret_key
'asecuresecretkey'
>>> production_secrets.db_password
'asecuredbpassword'
>>> production_secrets.pbkdf2_iterations_count
16384
```

## Author

*Keep It Secret* is developed by [Tomek Wójcik](https://www.bthlabs.pl/).

## License

*Keep It Secret* is licensed under the MIT License.
