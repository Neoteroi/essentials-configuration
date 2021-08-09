from abc import ABC, abstractmethod
from collections import abc
from typing import Any, Dict, List, Mapping, Optional

from .errors import ConfigurationOverrideError, MissingConfigurationError


def apply_key_value(obj, key, value):
    key = key.strip("_:")  # remove special characters from both ends
    for token in (":", "__"):
        if token in key:
            parts = key.split(token)

            sub_property = obj
            last_part = parts[-1]
            for part in parts[:-1]:

                if isinstance(sub_property, abc.MutableSequence):
                    try:
                        index = int(part)
                    except ValueError:
                        raise ConfigurationOverrideError(
                            f"{part} was supposed to be a numeric index in {key}"
                        )

                    sub_property = sub_property[index]
                    continue

                try:
                    sub_property = sub_property[part]
                except KeyError:
                    sub_property[part] = {}
                    sub_property = sub_property[part]
                else:
                    if not isinstance(sub_property, abc.Mapping) and not isinstance(
                        sub_property, abc.MutableSequence
                    ):
                        raise ConfigurationOverrideError(
                            f"The key `{key}` cannot be used "
                            f"because it overrides another "
                            f"variable with shorter key! ({part}, {sub_property})"
                        )

            if isinstance(sub_property, abc.MutableSequence):
                try:
                    index = int(last_part)
                except ValueError:
                    raise ConfigurationOverrideError(
                        f"{last_part} was supposed to be a numeric index in {key}, "
                        f"because the affected property is a mutable sequence."
                    )

                try:
                    sub_property[index] = value
                except IndexError:
                    raise ConfigurationOverrideError(
                        f"Invalid override for mutable sequence {key}; "
                        f"assignment index out of range"
                    )
            else:
                try:
                    sub_property[last_part] = value
                except TypeError as type_error:
                    raise ConfigurationOverrideError(
                        f"Invalid assignment {key} -> {value}; {str(type_error)}"
                    )

            return obj

    obj[key] = value
    return obj


def merge_values(destination, source):
    for key, value in source.items():
        apply_key_value(destination, key, value)


class ConfigurationSource(ABC):
    @abstractmethod
    def get_values(self) -> Dict[str, Any]:
        """Returns the values read from this source."""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class MapSource(ConfigurationSource):
    def __init__(self, values: Mapping[str, Any]) -> None:
        """
        Creates a configuration source that applies the given key-value mapping.
        """
        super().__init__()
        self._values = dict(values.items())

    def get_values(self) -> Dict[str, Any]:
        return self._values


class Configuration:
    """
    Provides methods to handle configuration objects.
    A read-only façade for navigating configuration objects using attribute notation.

    Thanks to Fluent Python, book by Luciano Ramalho; this class is inspired by his
    example of JSON structure explorer.
    """

    __slots__ = ("_data",)

    def __new__(cls, arg=None):
        if not arg:
            return super().__new__(cls)
        if isinstance(arg, abc.Mapping):
            return super().__new__(cls)
        if isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]
        return arg

    def __init__(self, mapping: Optional[Mapping[str, Any]] = None):
        """
        Creates a new instance of Configuration object with the given values.
        """
        self._data: Dict[str, Any] = dict(mapping.items()) if mapping else {}

    def __contains__(self, item: str) -> bool:
        return item in self._data

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __getattr__(self, name) -> Any:
        if name in self._data:
            value = self._data.get(name)
            if isinstance(value, abc.Mapping) or isinstance(value, abc.MutableSequence):
                return Configuration(value)  # type: ignore
            return value
        raise MissingConfigurationError(name)

    def __repr__(self) -> str:
        return f"<Configuration {repr(self._data)}>"

    @property
    def values(self) -> Dict[str, Any]:
        """
        Returns a copy of the dictionary of current settings.
        """
        return self._data.copy()


class ConfigurationBuilder:
    def __init__(self, sources: Optional[List[ConfigurationSource]] = None) -> None:
        """
        Creates a new instance of ConfigurationBuilder, that can obtain a Configuration
        object from different sources. Sources are applied in the given order and can
        override each other's settings.
        """
        self._sources: List[ConfigurationSource] = list(sources) if sources else []

    def __repr__(self) -> str:
        return f"<ConfigurationBuilder {self._sources}>"

    @property
    def sources(self) -> List[ConfigurationSource]:
        return self._sources

    def add_source(self, source: ConfigurationSource):
        self._sources.append(source)

    def add_map(self, values: Mapping[str, Any]):
        self.sources.append(MapSource(values))

    def add_value(self, key: str, value: Any):
        self.sources.append(MapSource({key: value}))

    def build(self) -> Configuration:
        settings = {}
        for source in self._sources:
            merge_values(settings, source.get_values())
        return Configuration(settings)
