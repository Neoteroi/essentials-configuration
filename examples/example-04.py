"""
This example illustrates a way to override settings from a common file, using an
environment specific settings file.
"""
import os
from dataclasses import dataclass

from config.common import ConfigurationBuilder
from config.yaml import YAMLFile


@dataclass
class OAuthSettings:
    app_id: str


# simulate an env variable..
os.environ["APP_ENVIRONMENT"] = "test"

environment_name = os.environ["APP_ENVIRONMENT"]

builder = ConfigurationBuilder(
    YAMLFile("./examples/example-04.yaml"),
    YAMLFile(f"./examples/example-04.{environment_name}.yaml", optional=True),
)

config = builder.build()

oauth_settings = config.bind(OAuthSettings, "oauth")

assert oauth_settings.app_id == "2222"  # overridden by ./examples/example-04.test.yaml
