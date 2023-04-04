import configparser
from collections import abc
from typing import Any, Dict

from config.common.files import FileConfigurationSource


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


class INIFile(FileConfigurationSource):
    def read_source(self) -> Dict[str, Any]:
        parser = configparser.ConfigParser()
        parser.read(self.file_path, encoding="utf8")
        return _develop_configparser_values(parser)
