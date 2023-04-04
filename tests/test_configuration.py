import os
from typing import Any, Dict

import pkg_resources
import pytest

from config.common import (
    Configuration,
    ConfigurationBuilder,
    ConfigurationSource,
    MapSource,
)
from config.env import EnvVars
from config.errors import ConfigurationOverrideError
from config.ini import INIFile
from config.json import JSONFile
from config.toml import TOMLFile
from config.yaml import YAMLFile


class FooSource(ConfigurationSource):
    def get_values(self) -> Dict[str, Any]:
        return {}


def _get_file_path(file_name: str) -> str:
    return pkg_resources.resource_filename(__name__, f"./{file_name}")


def test_builder():
    builder = ConfigurationBuilder()

    builder.add_map({"a": 1, "b": 2, "c": 3, "home": "foo"})

    conf = builder.build()

    assert conf.a == 1
    assert conf.b == 2
    assert conf.home == "foo"


def test_builder_add_value():
    builder = ConfigurationBuilder()

    builder.add_map({"a": 1, "b": 2, "c": 3, "home": "foo"})
    builder.add_value("a", 20)

    conf = builder.build()

    assert conf.a == 20
    assert conf.b == 2
    assert conf.home == "foo"


@pytest.mark.parametrize("keyword", ["for", "del", "async"])
def test_keywords_handling(keyword):
    config = Configuration({keyword: 1})
    assert config[keyword] == 1


def test_ini_file_1():
    builder = ConfigurationBuilder()

    builder.add_source(INIFile(_get_file_path("ini_example_01.ini")))

    config = builder.build()

    assert config.a.port == "8080"
    assert config.a.something == "hello"
    assert config.b.port == "50022"
    assert config.b.something == "world"


def test_ini_file_2():
    builder = ConfigurationBuilder()

    builder.add_source(INIFile(_get_file_path("ini_example_02.ini")))

    config = builder.build()

    # NB: support 'DEFAULT' magic section handled by built-in ConfigParser
    assert config.example.user == "hg"
    assert config.example.server_alive_interval == "45"
    assert config.example.compression == "yes"
    assert config.example.forward_x11 == "yes"
    assert config.example.utf8_check == "cześć"

    assert config.another.server_alive_interval == "45"
    assert config.another.compression == "yes"
    assert config.another.port == "50022"
    assert config.another.forward_x11 == "no"


def test_yaml_file_1():
    builder = ConfigurationBuilder()

    builder.add_source(YAMLFile(_get_file_path("./yaml_example_01.yaml")))

    config = builder.build()

    assert config.host == "localhost"
    assert config.port == 44555
    assert config.jwt_issuer == "https://example.org"
    assert config.jwt_audience == "https://example.org"
    assert config.jwt_algorithms == ["HS256"]


def test_yaml_file_2():
    builder = ConfigurationBuilder()

    builder.add_source(YAMLFile(_get_file_path("./yaml_example_02.yaml")))

    config = builder.build()

    assert config.foo[0].shares == -75.088
    assert config.foo[0].date == "11/27/2015"
    assert config.foo[1].shares == 75.088
    assert config.services.encryption.key == "SECRET_KEY"
    assert config.services.images.processor.type == "local"


def test_yaml_file_2_full_load():
    builder = ConfigurationBuilder()

    builder.add_source(
        YAMLFile(_get_file_path("./yaml_example_02.yaml"), safe_load=False)
    )

    config = builder.build()

    assert config.foo[0].shares == -75.088
    assert config.foo[0].date == "11/27/2015"
    assert config.foo[1].shares == 75.088
    assert config.services.encryption.key == "SECRET_KEY"
    assert config.services.images.processor.type == "local"


def test_toml_file_1():
    builder = ConfigurationBuilder()

    builder.add_source(TOMLFile(_get_file_path("./toml_example_01.toml")))

    config = builder.build()

    assert config.title == "TOML Example"
    assert config.owner.name == "Tom Preston-Werner"
    assert config.database.ports == [8000, 8001, 8002]
    assert config.servers.alpha.ip == "10.0.0.1"


def test_json_file_1():
    builder = ConfigurationBuilder()

    builder.add_source(JSONFile(_get_file_path("./json_example_01.json")))

    config = builder.build()

    assert (
        config.ApplicationInsights.InstrumentationKey
        == "742dc2e1-3f6f-447a-b710-6bf61d6e8a3c"
    )
    assert config.Authentication.B2C[0].IssuerName == "example"
    assert config.Logging.IncludeScopes is False

    for b2c_conf in config.Authentication.B2C:
        assert b2c_conf.IssuerName.startswith("example")


def test_dict_property_name():
    config = Configuration({"items": 200})

    assert config.items == 200


def test_list_item_as_configuration():
    config = Configuration({"items": [{"id": "1"}, {"id": "2"}]})

    first_item = config.items[0]
    assert isinstance(first_item, Configuration)
    assert first_item.id == "1"


def test_list_of_values():
    config = Configuration({"items": [{"id": "1"}, {"id": "2"}]})

    assert len(config.items) == 2
    assert config.items[0].id == "1"
    assert config.items[1].id == "2"


@pytest.mark.parametrize(
    "source,key,value,expected",
    [
        ({}, "a", 100, {"a": 100}),
        ({}, "message", "Hello World", {"message": "Hello World"}),
        ({}, "a:b", "Hello World", {"a": {"b": "Hello World"}}),
        ({}, "a:b:c", "Hello World", {"a": {"b": {"c": "Hello World"}}}),
        ({"a": ["Source"]}, "a:0", "Hello World", {"a": ["Hello World"]}),
        (
            {"a": {"b": ["Source"]}},
            "a:b:0",
            "Hello World",
            {"a": {"b": ["Hello World"]}},
        ),
    ],
)
def test_add_value(source, key, value, expected):
    builder = ConfigurationBuilder()

    builder.add_map(source)
    builder.add_map({key: value})

    config = builder.build()
    assert config.values == expected


@pytest.mark.parametrize(
    "source,key,value",
    [
        ({"a": []}, "a:0", "Hello World"),
        ({"a": ["Hello World"]}, "a:c", "Hello World"),
        ({"a": "Hello"}, "a:b:c", "Hello World"),
    ],
)
def test_apply_key_value_raises_for_invalid_overrides(source, key, value):
    builder = ConfigurationBuilder()
    builder.add_map(source)
    builder.add_map({key: value})

    with pytest.raises(ConfigurationOverrideError):
        builder.build()


def test_raises_attribute_error():
    configuration = Configuration({"foo": "foo"})

    assert configuration.foo == "foo"

    with pytest.raises(AttributeError):
        configuration.lorem_ipsum


def test_raises_key_error():
    configuration = Configuration({"foo": "foo"})

    assert configuration["foo"] == "foo"

    with pytest.raises(KeyError):
        configuration["lorem_ipsum"]


def test_raises_attribute_error_for_sub_property():
    configuration = Configuration({"section": {"one": True}})

    assert configuration.section.one is True

    with pytest.raises(AttributeError):
        configuration.section.two


@pytest.mark.parametrize(
    "configuration,expected_repr",
    [
        [
            Configuration({"section": {"one": True}}),
            "<Configuration {'section': '...'}>",
        ],
        [
            Configuration({"a": "Hello World"}),
            "<Configuration {'a': '...'}>",
        ],
        [
            Configuration(),
            "<Configuration {}>",
        ],
    ],
)
def test_configuration_repr(configuration, expected_repr):
    value = repr(configuration)
    assert value == expected_repr


def test_invalid_overriding_nested_list_item():
    builder = ConfigurationBuilder()
    builder.add_map({"ids": [1, 2, 3, 4, 5]})
    builder.add_map({"ids:1:foo": 6})

    with pytest.raises(ConfigurationOverrideError):
        builder.build()


def test_overriding_nested_list_values_raises_for_invalid_key():
    builder = ConfigurationBuilder()
    builder.add_map({"b2c": [{"tenant": "1"}, {"tenant": "2"}, {"tenant": "3"}]})
    builder.add_map({"b2c:foo:tenant": "4"})

    with pytest.raises(ConfigurationOverrideError):
        builder.build()


def test_contains():
    config = Configuration({"a": True})

    assert "a" in config
    assert "b" not in config


def test_configuration_source_repr():
    assert repr(FooSource()) == "<FooSource>"


def test_configuration_builder_repr():
    builder = ConfigurationBuilder()
    builder.add_source(FooSource())
    builder.add_source(EnvVars())
    assert (
        repr(builder) == "<ConfigurationBuilder [<FooSource>, <EnvironmentVariables>]>"
    )


@pytest.mark.parametrize(
    "source",
    [INIFile("noop.no"), YAMLFile("noop.no"), JSONFile("noop.no"), TOMLFile("noop.no")],
)
def test_file_source_raises_for_missing_file(source):
    builder = ConfigurationBuilder(source)

    with pytest.raises(FileNotFoundError):
        builder.build()


@pytest.mark.parametrize(
    "source",
    [INIFile("noop.no"), YAMLFile("noop.no"), JSONFile("noop.no"), TOMLFile("noop.no")],
)
def test_optional_file_source_does_not_raise_for_missing_file(source):
    source.optional = True
    builder = ConfigurationBuilder(source)
    builder.build()


def test_to_dictionary_method_after_applying_env():
    # in this test, environmental variables with TEST_ prefix are used
    # to override values from a previous source

    os.environ["TEST_b__c__d"] = "200"
    os.environ["TEST_a__0"] = "3"
    builder = ConfigurationBuilder(
        MapSource({"a": [1, 2, 3], "b": {"c": {"d": 100}}}),
        EnvVars("TEST_"),
    )

    config = builder.build()

    assert config.a[0] == "3"
    assert config.b.c.d == "200"
    assert config.values == {"a": ["3", 2, 3], "b": {"c": {"d": "200"}}}


def test_overriding_sub_properties():
    builder = ConfigurationBuilder(
        MapSource({"a": {"b": {"c": 100}}, "a2": "oof"}),
        MapSource({"a": {"b": {"c": 200}, "b2": "foo"}}),
    )

    config = builder.build()

    assert config.a.b.c == 200
    assert config.a.b2 == "foo"
    assert config.a2 == "oof"
