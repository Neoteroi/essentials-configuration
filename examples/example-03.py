"""
This example shows how to load app settings from a JSON file, and from
environment variables, filtered by "APP_" prefix and obtained from a .env file
(this is optional!), and how values can be overridden.
"""
from config.common import ConfigurationBuilder
from config.env import EnvVars
from config.json import JSONFile

builder = ConfigurationBuilder(
    JSONFile("./examples/settings.json"),
    EnvVars(file="./examples/example-03.env", prefix="APP_"),
)

config = builder.build()

# The following value comes from ./examples/settings.json
assert config.foo == "foo"

# The following value is because the env variables in ./examples/example-03.env
# override the setting in ./examples/settings.json
assert config.logging.level == "DEBUG"
