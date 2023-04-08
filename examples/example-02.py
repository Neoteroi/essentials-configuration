"""
This example shows how to load app settings from a TOML file, and from
environment variables, filtered by "APP_" prefix.
"""
from config.common import ConfigurationBuilder
from config.env import EnvVars
from config.toml import TOMLFile

builder = ConfigurationBuilder(
    TOMLFile("./examples/settings.toml"),
    EnvVars(prefix="APP_"),
)

config = builder.build()

assert config.project.name == "essentials-configuration"
assert config.project.version == "2.0.0"
assert config.project.authors[0].name == "Roberto Prevato"
