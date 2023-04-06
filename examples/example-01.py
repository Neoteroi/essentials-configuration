"""
This example illustrates how data can be fetched from a source (YAMLFile) and read
into an instance of a specific type (FooSettings), validated using pydantic.

This example has a single source for the sake of simplicity, but in normal situations
several layers would be used (e.g. settings file, env specific settings file, env
variables, etc.).
"""

from pydantic import BaseModel

from config.common import ConfigurationBuilder
from config.yaml import YAMLFile


class FooSettings(BaseModel):
    value: str
    x: int


builder = ConfigurationBuilder(YAMLFile("./examples/example-01.yaml"))

config = builder.build()

foo_settings = config.bind(FooSettings, "foo")

assert isinstance(foo_settings, FooSettings)
assert foo_settings.value == "foo"
assert foo_settings.x == 100
