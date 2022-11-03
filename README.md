![Build](https://github.com/Neoteroi/essentials-configuration/workflows/Build/badge.svg)
[![pypi](https://img.shields.io/pypi/v/essentials-configuration.svg)](https://pypi.python.org/pypi/essentials-configuration)
[![versions](https://img.shields.io/pypi/pyversions/essentials-configuration.svg)](https://github.com/Neoteroi/essentials-configuration)
[![codecov](https://codecov.io/gh/Neoteroi/essentials-configuration/branch/main/graph/badge.svg?token=VzAnusWIZt)](https://codecov.io/gh/Neoteroi/essentials-configuration)
[![license](https://img.shields.io/github/license/Neoteroi/essentials-configuration.svg)](https://github.com/Neoteroi/essentials-configuration/blob/main/LICENSE)

# Python configuration utilities
Implementation of key-value pair based configuration for Python applications.

**Features:**
* support for most common sources of application settings
* support for overriding settings in sequence
* support for nested structures and lists, using attribute notation
* strategy to use environment specific settings

This library is freely inspired by .NET Core `Microsoft.Extensions.Configuration` (_ref. [MSDN documentation](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/configuration/?view=aspnetcore-2.1), [Microsoft Extensions Configuration Deep Dive](https://www.paraesthesia.com/archive/2018/06/20/microsoft-extensions-configuration-deep-dive/)_).

The main class is influenced by Luciano Ramalho`s example of
JSON structure explorer using attribute notation, in his book [Fluent Python](http://shop.oreilly.com/product/0636920032519.do).

## Overview

`essentials-configuration` provides a way to handle configuration roots
composed of different layers, such as configuration files and environment
variables. Layers are applied in order and can override each others' values,
enabling different scenarios like configuration by environment and system
instance.

## Supported sources:
* **toml** files
* **yaml** files
* **json** files
* **ini** files
* environment variables
* dictionaries
* keys and values
* [Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/general/basic-concepts), using [essentials-configuration-keyvault](https://github.com/Neoteroi/essentials-configuration-keyvault)
* custom sources, implementing the `ConfigurationSource` interface

## Installation

```bash
pip install essentials-configuration
```

To install with support for `YAML` configuration files:

```
pip install essentials-configuration[yaml]
```

## Extensions

* Azure Key Vault secrets configuration source:
  [essentials-configuration-keyvault](https://github.com/Neoteroi/essentials-configuration-keyvault)


# Examples

### JSON file and environment variables

In the following example, configuration values will include the structure
inside the file `settings.json` and environment variables whose name starts
with "APP_". Settings are applied in order, so environment variables with
matching name override values from the `json` file.

```python
from configuration.common import ConfigurationBuilder
from configuration.json import JSONFile
from configuration.env import EnvVars

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
from configuration.common import ConfigurationBuilder
from configuration.env import EnvVars
from configuration.yaml import YAMLFile

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

from configuration.common import ConfigurationBuilder
from configuration.env import EnvVars
from configuration.yaml import YAMLFile

environment_name = os.environ["APP_ENVIRONMENT"]

builder = ConfigurationBuilder()

builder.add_source(YAMLFile("settings.yaml"))

builder.add_source(YAMLFile(f"settings.{environment_name}.yaml", optional=True))

builder.add_source(EnvVars(prefix="APP_"))

config = builder.build()
```

### Filtering environment variables by prefix

```python
from configuration.common import ConfigurationBuilder
from configuration.env import EnvVars

builder = ConfigurationBuilder()

builder.add_source(EnvVars(prefix="APP_"))

config = builder.build()
```

### INI files

INI files are parsed using the built-in `configparser` module, therefore
support `[DEFAULT]` section; all values are kept as strings.

```python
from configuration.common import ConfigurationBuilder
from configuration.ini import INIFile

builder = ConfigurationBuilder()

builder.add_source(INIFile("settings.ini"))

config = builder.build()
```

### Dictionaries

```python
from configuration.common import ConfigurationBuilder

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
from configuration.common import ConfigurationBuilder

builder = ConfigurationBuilder()

builder.add_map({"host": "localhost", "port": 8080})

builder.add_value("port", 44555)

config = builder.build()

assert config.host == "localhost"
assert config.port == 44555
```

### Overriding nested values

It is possible to override nested values by environment variables or
dictionary keys using the following notation for sub properties:

* keys separated by colon ":", such as `a:d:e`
* keys separated by "__", such as `a__d__e`

```python
from configuration.common import ConfigurationBuilder, MapSource


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

builder = ConfigurationBuilder(
    MapSource(
        {
            "a": {Env
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
builder = ConfigurationBuilder(
    MapSource(
        {
            "b2c": [
                {"tenant": "1"},
                {"tenant": "2"},
                {"tenant": "3"},
            ]
        }
    )
)

builder.add_value("b2c:1:tenant", "4")

config = builder.build()

assert config.b2c[0].tenant == "1"
assert config.b2c[1].tenant == "4"
assert config.b2c[2].tenant == "3"

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
