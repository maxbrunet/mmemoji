from mmemoji.cli import cli
from mmemoji.version import VERSION


def test_help(cli_runner):
    result = cli_runner.invoke(cli, ["--help"])
    assert result.exit_code == 0


def test_version(cli_runner):
    result = cli_runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output == "mmemoji {}\n".format(VERSION)


def test_unknown_command(cli_runner):
    result = cli_runner.invoke(cli, ["unknown"])
    assert result.exit_code == 1
    assert (
        result.stderr == 'Error: Unknown command "unknown" for "mmemoji"\n'
        "Run 'mmemoji --help' for usage.\n"
    )
