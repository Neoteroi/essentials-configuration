class ConfigurationError(Exception):
    """An exception risen for invalid configuration."""


class ConfigurationOverrideError(ConfigurationError):
    """An exception risen for invalid configuration override."""


class MissingConfigurationFileError(ConfigurationError, FileNotFoundError):
    def __init__(self, file_path: str) -> None:
        super().__init__(f"Missing configuration file: {file_path}")
        self.missing_file_path = file_path
