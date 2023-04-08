![Build](https://github.com/Neoteroi/essentials-configuration/workflows/Build/badge.svg)
[![pypi](https://img.shields.io/pypi/v/essentials-configuration.svg)](https://pypi.python.org/pypi/essentials-configuration)
[![versions](https://img.shields.io/pypi/pyversions/essentials-configuration.svg)](https://github.com/Neoteroi/essentials-configuration)
[![codecov](https://codecov.io/gh/Neoteroi/essentials-configuration/branch/main/graph/badge.svg?token=VzAnusWIZt)](https://codecov.io/gh/Neoteroi/essentials-configuration)
[![license](https://img.shields.io/github/license/Neoteroi/essentials-configuration.svg)](https://github.com/Neoteroi/essentials-configuration/blob/main/LICENSE)

# Python configuration utilities
Implementation of key-value pair based configuration for Python applications.

**Features:**
- support for most common sources of application settings
- support for overriding settings in sequence
- support for nested structures and lists, using attribute notation
- strategy to use environment specific settings
- features to handle secrets and values stored in the user folder, for local
  development
- features to support validation of configuration items, for example using
  `pydantic`, or user defined classes

This library is freely inspired by .NET Core `Microsoft.Extensions.Configuration` (_ref. [MSDN documentation](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/configuration/?view=aspnetcore-2.1), [Microsoft Extensions Configuration Deep Dive](https://www.paraesthesia.com/archive/2018/06/20/microsoft-extensions-configuration-deep-dive/)_).

The main class is influenced by Luciano Ramalho`s example of
JSON structure explorer using attribute notation, in his book [Fluent Python](http://shop.oreilly.com/product/0636920032519.do).

## Overview

`essentials-configuration` provides a way to handle configuration roots
composed of several layers, such as configuration files and environment
variables. Layers are applied in order and can override each others' values,
enabling different scenarios like configuration by environment and system
instance.

## Supported sources:
- **toml** files
- **yaml** files
- **json** files
- **ini** files
- environment variables
- secrets stored in the user folder, for development purpose
- dictionaries
- keys and values
- [Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/general/basic-concepts), using [essentials-configuration-keyvault](https://github.com/Neoteroi/essentials-configuration-keyvault)
- custom sources, implementing the `ConfigurationSource` interface

## Installation

```bash
pip install essentials-configuration
```

To install with support for `YAML` configuration files:

```
pip install essentials-configuration[yaml]
```

To install with support for `YAML` configuration files and the `CLI` to handle
user secrets:

```
pip install essentials-configuration[full]
```

## Extensions

* Azure Key Vault secrets configuration source:
  [essentials-configuration-keyvault](https://github.com/Neoteroi/essentials-configuration-keyvault)

# Examples

Please read the list of examples in the [examples folder](./examples). Below
are reported some of the examples that are tested in this repository.

### TOML file

```python
from config.common import ConfigurationBuilder
from config.env import EnvVars
from config.toml import TOMLFile


builder = ConfigurationBuilder(
    TOMLFile("settings.toml"),
    EnvVars(prefix="APP_")
)

config = builder.build()
```

For example, if the TOML file contains the following contents:

```toml
title = "TOML Example"

[owner]
name = "Tom Preston-Werner"
```

And the environment has a variable such as `APP_OWNER__NAME=AAA`, the owner
name from the TOML file gets overridden by the env variable:

```python
>>> config
<Configuration {'title': '...', 'owner': '...'}>
>>> config.title
'TOML Example'
>>> config.owner.name
'AAA'
```

### JSON file and environment variables

In the following example, configuration values will include the structure
inside the file `settings.json` and environment variables whose name starts
with "APP_". Settings are applied in order, so environment variables with
matching name override values from the `json` file.

```python
from config.common import ConfigurationBuilder
from config.json import JSONFile
from config.env import EnvVars

builder = ConfigurationBuilder(
    JSONFile("settings.json"),
    EnvVars(prefix="APP_")
)

config = builder.build()
```

For example, if the JSON file contains the following contents:

```json
{
    "logging": {
        "level": "INFO"
    },
    "example": "Hello World",
    "foo": "foo"
}
```

And the environment has a variable named `APP_foo=AAA`:

```python
>>> config
<Configuration {'logging': '...', 'example': '...', 'foo': '...'}>
>>> config.foo
'AAA'
>>> config.logging.level
'INFO'
```

### YAML file and environment variables

In this example, configuration will include anything inside a file
`settings.yaml` and environment variables. Settings are applied in order, so
environment variables with matching name override values from the `yaml` file
(using the `yaml` source requires also `PyYAML` package).


```python
from config.common import ConfigurationBuilder
from config.env import EnvVars
from config.yaml import YAMLFile

builder = ConfigurationBuilder()

builder.add_source(YAMLFile("settings.yaml"))
builder.add_source(EnvVars())

config = builder.build()
```

### YAML file, optional file by environment

In this example, if an environment variable with name `APP_ENVIRONMENT` and
value `dev` exists, and a configuration file with name `settings.dev.yaml` is
present, it is read to override values configured in `settings.yaml` file.

```python
import os

from config.common import ConfigurationBuilder
from config.env import EnvVars
from config.yaml import YAMLFile

environment_name = os.environ["APP_ENVIRONMENT"]

builder = ConfigurationBuilder(
    YAMLFile("settings.yaml"),
    YAMLFile(f"settings.{environment_name}.yaml", optional=True)
)

config = builder.build()
```

### Filtering environment variables by prefix

```python
from config.common import ConfigurationBuilder
from config.env import EnvVars

builder = ConfigurationBuilder()

builder.add_source(EnvVars(prefix="APP_"))

config = builder.build()
```

### INI files

INI files are parsed using the built-in `configparser` module, therefore
support `[DEFAULT]` section; all values are kept as strings.

```python
from config.common import ConfigurationBuilder
from config.ini import INIFile

builder = ConfigurationBuilder()

builder.add_source(INIFile("settings.ini"))

config = builder.build()
```

### Dictionaries

```python
from config.common import ConfigurationBuilder

builder = ConfigurationBuilder()

builder.add_map({"host": "localhost", "port": 8080})

builder.add_map({"hello": "world", "example": [{"id": 1}, {"id": 2}]})

config = builder.build()

assert config.host == "localhost"
assert config.port == 8080
assert config.hello == "world"
assert config.example[0].id == 1
assert config.example[1].id == 2
```

### Keys and values

```python
from config.common import ConfigurationBuilder

builder = ConfigurationBuilder()

builder.add_map({"host": "localhost", "port": 8080})

builder.add_value("port", 44555)

config = builder.build()

assert config.host == "localhost"
assert config.port == 44555
```

### User secrets

The library provides a strategy to handle secrets during local development,
storing them into the user folder.

The following example shows how secrets can be configured for a project:

```bash
config secrets init
config secrets set "Foo" "Some secret value"
```

Secrets are organized by project, and the project information is obtained from
`pyproject.toml` files (from the `project.name` property). If `pyproject.toml`
file does not exist, one is generated automatically with a random name.

---

Then, from a Python app, it's possible to load the secrets from the user folder:

```python
from config.common import ConfigurationBuilder
from config.json import JSONFile
from config.secrets import UserSecrets

builder = ConfigurationBuilder(JSONFile("settings.json"), UserSecrets())

config = builder.build()

print(config)
# config contains both values from `settings.json`, and secrets read from the user
# folder
```

Secrets are optional and should be used only for local development, they are
stored in unencrypted form in the user's folder.

Production apps should use dedicated services to handle secrets, like
[Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/general/basic-concepts),
[AWS Secrets Manager](https://aws.amazon.com/secrets-manager/), or similar services.
For Azure Key Vault, an implementation is provided in [essentials-configuration-keyvault](https://github.com/Neoteroi/essentials-configuration-keyvault).

## Handling user secrets

User secrets can be handled using the provided `config` CLI.

```
config secrets
Usage: config secrets [OPTIONS] COMMAND [ARGS]...

  Commands to handle user secrets, for local development.

Options:
  --help  Show this message and exit.

Commands:
  del       Delete a secret for a project, by key.
  get       Get a secret in a user file by key.
  info      Show information about secrets for a project.
  init      Initialize user secrets for the current folder.
  list      List all projects configured for secrets stored in the user...
  set       Set a secret in a user file by key and value.
  set-many  Set many secrets read from a JSON file passed through stdin.
  show      Show the local secrets for a project.
```

### Overriding nested values

It is possible to override nested values by environment variables or
dictionary keys using the following notation for sub properties:

* keys separated by colon ":", such as `a:d:e`
* keys separated by "__", such as `a__d__e`

```python
from config.common import ConfigurationBuilder, MapSource


builder = ConfigurationBuilder(
    MapSource(
        {
            "a": {
                "b": 1,
                "c": 2,
                "d": {
                    "e": 3,
                    "f": 4,
                },
            }
        }
    )
)

config = builder.build()

assert config.a.b == 1
assert config.a.d.e == 3
assert config.a.d.f == 4

builder.add_value("a:d:e", 5)

config = builder.build()

assert config.a.d.e == 5
assert config.a.d.f == 4

```

### Overriding nested values using env variables

```python
import os

from config.common import ConfigurationBuilder, MapSource
from config.env import EnvVars

builder = ConfigurationBuilder(
    MapSource(
        {
            "a": {
                "b": 1,
                "c": 2,
                "d": {
                    "e": 3,
                    "f": 4,
                },
            }
        }
    )
)

config = builder.build()

assert config.a.b == 1
assert config.a.d.e == 3
assert config.a.d.f == 4

# NB: if an env variable such as:
# a:d:e=5
# or...
# a__d__e=5
#
# is defined, it overrides the value  from the dictionary

os.environ["a__d__e"] = "5"

builder.sources.append(EnvVars())

config = builder.build()

assert config.a.d.e == "5"
```

### Overriding values in list items using env variables

```python
import os

from config.common import ConfigurationBuilder, MapSource
from config.env import EnvVars

builder = ConfigurationBuilder(
    MapSource(
        {
            "b2c": [
                {"tenant": "1"},
                {"tenant": "2"},
                {"tenant": "3"},
            ]
        }
    ),
    EnvVars(),
)

os.environ["b2c__0__tenant"] = "5"

config = builder.build()

assert config.b2c[0].tenant == "5"
assert config.b2c[1].tenant == "2"
assert config.b2c[2].tenant == "3"
```

### Typed config

To bind configuration sections with types checking, for example to use `pydantic` to
validate application settings, use the `config.bind` method like in
the following example:

```yaml
# example-01.yaml
foo:
  value: "foo"
  x: 100
```

```python
# example
from pydantic import BaseModel

from config.common import ConfigurationBuilder
from config.yaml import YAMLFile


class FooSettings(BaseModel):
    value: str
    x: int


builder = ConfigurationBuilder(YAMLFile("example-01.yaml"))

config = builder.build()

# the bind method accepts a variable number of fragments to
# obtain the configuration section that should be used to instantiate the given type
foo_settings = config.bind(FooSettings, "foo")

assert isinstance(foo_settings, FooSettings)
assert foo_settings.value == "foo"
assert foo_settings.x == 100
```

### Goal and non-goals

The goal of this package is to provide a way to handle configuration roots,
fetching and composing settings from different sources, usually happening
once at application's start.

The library implements only a synchronous API and fetching of application
settings atomically (it doesn't support generators), like application settings
fetched from INI, JSON, or YAML files that are read once in memory entirely.
An asynchronous API is currently out of the scope of this library, since its
primary use case is to fetch configuration values once at application's start.
