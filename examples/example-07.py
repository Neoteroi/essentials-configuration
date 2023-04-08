"""
This example shows how to override nested properties using environment
variables.
"""
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
