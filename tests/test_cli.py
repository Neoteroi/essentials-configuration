import os
import json
from uuid import uuid4

import pytest
from click.testing import CliRunner

from config.cli.main import main
from config.secrets.cli import (
    init_secrets,
    list_groups,
    set_many_secrets,
    set_secret,
    show_info,
    show_secrets,
)


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
    result = runner.invoke(init_secrets, ["-p", test_id])
    assert result.exit_code == 0


def test_show_info():
    test_id = uuid4().hex
    runner = CliRunner()
    result = runner.invoke(show_info, ["-p", test_id])
    assert result.exit_code == 0
    assert result.output == "There is no secrets file configured.\n"

    result = runner.invoke(init_secrets, ["-p", test_id])
    assert result.exit_code == 0
    assert result.output == "Initialized project secrets for: %s\n" % test_id


def test_set_secret_show_secrets():
    test_id = uuid4().hex
    runner = CliRunner()
    result = runner.invoke(init_secrets, ["-p", test_id])
    assert result.exit_code == 0

    result = runner.invoke(set_secret, ["Foo", "FOO", "-p", test_id])
    assert result.exit_code == 0

    result = runner.invoke(show_secrets, ["-p", test_id])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == {"Foo": "FOO"}


def test_set_secret_verbose():
    test_id = uuid4().hex
    runner = CliRunner()
    result = runner.invoke(init_secrets, ["-p", test_id])
    assert result.exit_code == 0

    result = runner.invoke(
        main, ["--verbose", "secrets", "set", "Foo", "FOO", "-p", test_id]
    )
    assert result.exit_code == 0

    result = runner.invoke(show_secrets, ["-p", test_id])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data == {"Foo": "FOO"}
