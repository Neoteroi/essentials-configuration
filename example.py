from config.common import ConfigurationBuilder
from config.json import JSONFile
from config.secrets import UserSecrets

builder = ConfigurationBuilder(JSONFile("settings.json"), UserSecrets())

config = builder.build()

print(config)
# config contains both values from `settings.json`, and secrets read from the user
# folder
