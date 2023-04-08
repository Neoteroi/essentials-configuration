"""
This example shows how nested values can be overridden using strings.
"""
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
