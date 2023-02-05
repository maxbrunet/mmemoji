from click.testing import CliRunner

from mmemoji import __version__
from mmemoji.cli import cli


def test_help(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(cli, ["--help"])
    assert result.exit_code == 0


def test_version(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"mmemoji {__version__}\n"


def test_unknown_command(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(cli, ["unknown"])
    assert result.exit_code == 1
    assert (
        result.stderr == 'Error: Unknown command "unknown" for "mmemoji"\n'
        "Run 'mmemoji --help' for usage.\n"
    )
