import json
import os
from uuid import uuid4

import pytest
from click.testing import CliRunner

from config.cli.main import main


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
