import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import pytest
from click.testing import CliRunner

from config.cli.main import main


@contextmanager
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dirname:
        prev_dir = os.getcwd()
        os.chdir(os.path.expanduser(temp_dirname))
        try:
            yield Path(temp_dirname)
        finally:
            os.chdir(prev_dir)


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 0


@pytest.fixture
def restore_env():
    yield
    del os.environ["EC_VERBOSE"]


def test_main_verbose(restore_env):
    runner = CliRunner()
    result = runner.invoke(main, ["--verbose", "settings", "info"])
    assert result.exit_code == 0
    assert os.environ.get("EC_VERBOSE") == "1"


def test_init_settings():
    test_id = uuid4().hex
    runner = CliRunner()
    result = runner.invoke(main, ["settings", "init", "-p", test_id])
    assert result.exit_code == 0


def test_show_info():
    test_id = uuid4().hex
    runner = CliRunner()
    result = runner.invoke(main, ["settings", "info", "-p", test_id])
    assert result.exit_code == 0
    assert result.output == "There is no settings file configured.\n"

    result = runner.invoke(main, ["settings", "init", "-p", test_id])
    assert result.exit_code == 0
    assert result.output == "Initialized project settings for: %s\n" % test_id


def test_set_value_show_settings():
    test_id = uuid4().hex
    runner = CliRunner()
    result = runner.invoke(main, ["settings", "init", "-p", test_id])
    assert result.exit_code == 0

    result = runner.invoke(main, ["settings", "set", "Foo", "FOO", "-p", test_id])
    assert result.exit_code == 0

    result = runner.invoke(main, ["settings", "show", "-p", test_id])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == {"Foo": "FOO"}


@pytest.mark.parametrize("sep", ["__", "."])
def test_set_value_nested_show_settings(sep):
    test_id = uuid4().hex
    runner = CliRunner()
    result = runner.invoke(main, ["settings", "init", "-p", test_id])
    assert result.exit_code == 0

    result = runner.invoke(
        main, ["settings", "set", f"source{sep}one", "foo", "-p", test_id]
    )
    result = runner.invoke(
        main, ["settings", "set", f"source{sep}two", "ufo", "-p", test_id]
    )

    result = runner.invoke(main, ["settings", "show", "-p", test_id])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == {"source": {"one": "foo", "two": "ufo"}}


def test_set_value_verbose():
    test_id = uuid4().hex
    runner = CliRunner()
    result = runner.invoke(main, ["settings", "init", "-p", test_id])
    assert result.exit_code == 0

    result = runner.invoke(
        main, ["--verbose", "settings", "set", "Foo", "FOO", "-p", test_id]
    )
    assert result.exit_code == 0

    result = runner.invoke(main, ["settings", "show", "-p", test_id])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == {"Foo": "FOO"}


def test_list_groups():
    runner = CliRunner()
    result = runner.invoke(main, ["settings", "list"])
    assert result.exit_code == 0


def test_set_many_settings_main():
    runner = CliRunner()
    result = runner.invoke(main, ["settings", "set-many"])
    assert result.exit_code == 1


def test_settings_init_generate_pyproject():
    with temp_dir() as temp_dirname:
        runner = CliRunner()
        result = runner.invoke(main, ["settings", "init"])
        assert result.exit_code == 0
        generated_pyproj = Path(temp_dirname) / "pyproject.toml"
        assert generated_pyproj.exists()


def test_settings_set_value_generate_pyproject():
    with temp_dir() as temp_dirname:
        runner = CliRunner()
        result = runner.invoke(main, ["settings", "set", "Foo", "FOO"])
        assert result.exit_code == 0
        generated_pyproj = Path(temp_dirname) / "pyproject.toml"
        assert generated_pyproj.exists()


def test_set_value_show_settings_auto_project():
    with temp_dir():
        runner = CliRunner()
        result = runner.invoke(main, ["settings", "init"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["settings", "set", "Foo", "FOO"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["settings", "show"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == {"Foo": "FOO"}


def test_get_value_auto_project():
    with temp_dir():
        runner = CliRunner()
        result = runner.invoke(main, ["settings", "init"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["settings", "set", "AAA", "Hello World"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["settings", "get", "AAA"])
        assert result.exit_code == 0
        assert result.output == "Hello World\n"


def test_set_value_del_value_auto_project():
    with temp_dir():
        runner = CliRunner()
        result = runner.invoke(main, ["settings", "init"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["settings", "set", "Foo", "FOO"])
        result = runner.invoke(main, ["settings", "set", "SendGridAPIKey", "******"])

        result = runner.invoke(main, ["settings", "show"])
        data = json.loads(result.output)
        assert data == {"Foo": "FOO", "SendGridAPIKey": "******"}

        result = runner.invoke(main, ["settings", "del", "Foo"])
        result = runner.invoke(main, ["settings", "show"])
        data = json.loads(result.output)
        assert data == {"SendGridAPIKey": "******"}


def test_set_value_del_not_existing_value_auto_project():
    with temp_dir():
        runner = CliRunner()
        result = runner.invoke(main, ["settings", "init"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["settings", "set", "Foo", "FOO"])

        result = runner.invoke(main, ["settings", "show"])
        data = json.loads(result.output)
        assert data == {"Foo": "FOO"}

        result = runner.invoke(main, ["settings", "del", "UFO"])
        result = runner.invoke(main, ["settings", "show"])
        data = json.loads(result.output)
        assert data == {"Foo": "FOO"}


def test_del_value_no_settings_auto_project():
    with temp_dir():
        runner = CliRunner()
        result = runner.invoke(main, ["settings", "del", "Foo"])
        assert result.exit_code == 0


def test_set_many_settings_show_settings_auto_project():
    with temp_dir() as folder:
        initial_data = {
            "SomeSecret": "Hello, There!",
            "SendGridAPIKey": "******",
            "BlaBla": "Bla",
        }
        source = folder / "source.json"
        source.write_text(json.dumps(initial_data, indent=4), encoding="utf8")

        runner = CliRunner()
        result = runner.invoke(main, ["settings", "init"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["settings", "set-many", "--file", "source.json"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["settings", "show"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == initial_data
