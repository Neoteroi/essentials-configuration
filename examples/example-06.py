"""
This example shows how to override nested properties in arrays using
environment variables.
"""

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
