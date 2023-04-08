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
    result = runner.invoke(main, ["--verbose", "secrets", "info"])
    assert result.exit_code == 0
    assert os.environ.get("EC_VERBOSE") == "1"


def test_init_secrets():
    test_id = uuid4().hex
    runner = CliRunner()
    result = runner.invoke(main, ["secrets", "init", "-p", test_id])
    assert result.exit_code == 0


def test_show_info():
    test_id = uuid4().hex
    runner = CliRunner()
    result = runner.invoke(main, ["secrets", "info", "-p", test_id])
    assert result.exit_code == 0
    assert result.output == "There is no secrets file configured.\n"

    result = runner.invoke(main, ["secrets", "init", "-p", test_id])
    assert result.exit_code == 0
    assert result.output == "Initialized project secrets for: %s\n" % test_id


def test_set_secret_show_secrets():
    test_id = uuid4().hex
    runner = CliRunner()
    result = runner.invoke(main, ["secrets", "init", "-p", test_id])
    assert result.exit_code == 0

    result = runner.invoke(main, ["secrets", "set", "Foo", "FOO", "-p", test_id])
    assert result.exit_code == 0

    result = runner.invoke(main, ["secrets", "show", "-p", test_id])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == {"Foo": "FOO"}


def test_set_secret_verbose():
    test_id = uuid4().hex
    runner = CliRunner()
    result = runner.invoke(main, ["secrets", "init", "-p", test_id])
    assert result.exit_code == 0

    result = runner.invoke(
        main, ["--verbose", "secrets", "set", "Foo", "FOO", "-p", test_id]
    )
    assert result.exit_code == 0

    result = runner.invoke(main, ["secrets", "show", "-p", test_id])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == {"Foo": "FOO"}


def test_list_groups():
    runner = CliRunner()
    result = runner.invoke(main, ["secrets", "list"])
    assert result.exit_code == 0


def test_set_many_secrets_main():
    runner = CliRunner()
    result = runner.invoke(main, ["secrets", "set-many"])
    assert result.exit_code == 1


def test_secrets_init_generate_pyproject():
    with temp_dir() as temp_dirname:
        runner = CliRunner()
        result = runner.invoke(main, ["secrets", "init"])
        assert result.exit_code == 0
        generated_pyproj = Path(temp_dirname) / "pyproject.toml"
        assert generated_pyproj.exists()


def test_secrets_set_secret_generate_pyproject():
    with temp_dir() as temp_dirname:
        runner = CliRunner()
        result = runner.invoke(main, ["secrets", "set", "Foo", "FOO"])
        assert result.exit_code == 0
        generated_pyproj = Path(temp_dirname) / "pyproject.toml"
        assert generated_pyproj.exists()


def test_set_secret_show_secrets_auto_project():
    with temp_dir():
        runner = CliRunner()
        result = runner.invoke(main, ["secrets", "init"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["secrets", "set", "Foo", "FOO"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["secrets", "show"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == {"Foo": "FOO"}


def test_get_secret_auto_project():
    with temp_dir():
        runner = CliRunner()
        result = runner.invoke(main, ["secrets", "init"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["secrets", "set", "AAA", "Hello World"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["secrets", "get", "AAA"])
        assert result.exit_code == 0
        assert result.output == "Hello World\n"


def test_set_secret_del_secret_auto_project():
    with temp_dir():
        runner = CliRunner()
        result = runner.invoke(main, ["secrets", "init"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["secrets", "set", "Foo", "FOO"])
        result = runner.invoke(main, ["secrets", "set", "SendGridAPIKey", "******"])

        result = runner.invoke(main, ["secrets", "show"])
        data = json.loads(result.output)
        assert data == {"Foo": "FOO", "SendGridAPIKey": "******"}

        result = runner.invoke(main, ["secrets", "del", "Foo"])
        result = runner.invoke(main, ["secrets", "show"])
        data = json.loads(result.output)
        assert data == {"SendGridAPIKey": "******"}


def test_set_secret_del_not_existing_secret_auto_project():
    with temp_dir():
        runner = CliRunner()
        result = runner.invoke(main, ["secrets", "init"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["secrets", "set", "Foo", "FOO"])

        result = runner.invoke(main, ["secrets", "show"])
        data = json.loads(result.output)
        assert data == {"Foo": "FOO"}

        result = runner.invoke(main, ["secrets", "del", "UFO"])
        result = runner.invoke(main, ["secrets", "show"])
        data = json.loads(result.output)
        assert data == {"Foo": "FOO"}


def test_del_secret_no_secrets_auto_project():
    with temp_dir():
        runner = CliRunner()
        result = runner.invoke(main, ["secrets", "del", "Foo"])
        assert result.exit_code == 0


def test_set_many_secrets_show_secrets_auto_project():
    with temp_dir() as folder:
        initial_data = {
            "SomeSecret": "Hello, There!",
            "SendGridAPIKey": "******",
            "BlaBla": "Bla",
        }
        source = folder / "source.json"
        source.write_text(json.dumps(initial_data, indent=4), encoding="utf8")

        runner = CliRunner()
        result = runner.invoke(main, ["secrets", "init"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["secrets", "set-many", "--file", "source.json"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["secrets", "show"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == initial_data
