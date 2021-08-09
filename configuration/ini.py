import configparser
import os
from collections import abc
from typing import Any, Dict

from . import ConfigurationSource
from .errors import MissingConfigurationFileError


def _develop_configparser_values(parser):
    values = {}
    for section_name in parser.sections():
        section_values = {}
        for key, value in parser[section_name].items():
            section_values[key] = (
                _develop_configparser_values(value)
                if isinstance(value, abc.Mapping)
                else value
            )
        values[section_name] = section_values
    return values


class INIFile(ConfigurationSource):
    def __init__(self, file_path: str, optional: bool = False) -> None:
        """
        Creates a new instance of INIFileSource, to read configuration from the INI
        file at the given path. If optional, nothing is returned if the file is not
        found.
        """
        super().__init__()
        self.file_path = file_path
        self.optional = optional

    def get_values(self) -> Dict[str, Any]:
        if not os.path.exists(self.file_path):
            if self.optional:
                return {}
            raise MissingConfigurationFileError(self.file_path)

        parser = configparser.ConfigParser()
        parser.read(self.file_path)
        return _develop_configparser_values(parser)
