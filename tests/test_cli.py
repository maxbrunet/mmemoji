from click.testing import CliRunner

from mmemoji.cli import cli
from mmemoji.version import VERSION


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output == "mmemoji {}\n".format(VERSION)
