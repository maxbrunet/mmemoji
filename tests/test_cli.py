import pytest
from click.testing import CliRunner

from mmemoji import __version__
from mmemoji.cli import cli


@pytest.mark.usefixtures("class_utils")
class TestCli:
    cli_runner: CliRunner

    def test_help(self) -> None:
        result = self.cli_runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

    def test_version(self) -> None:
        result = self.cli_runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output == f"mmemoji {__version__}\n"

    def test_unknown_command(self) -> None:
        result = self.cli_runner.invoke(cli, ["unknown"])
        assert result.exit_code == 1
        assert (
            result.stderr == 'Error: Unknown command "unknown" for "mmemoji"\n'
            "Run 'mmemoji --help' for usage.\n"
        )

    def test_broken_command_dependency_not_masked(self, monkeypatch) -> None:
        import importlib.abc
        import sys

        from click import Context

        class _BlockTabulate(importlib.abc.MetaPathFinder):
            def find_spec(self, name, path=None, target=None):
                if name == "tabulate":
                    raise ModuleNotFoundError("No module named 'tabulate'")
                return None

        monkeypatch.delitem(sys.modules, "mmemoji.commands.list", raising=False)
        monkeypatch.delitem(sys.modules, "mmemoji.decorators", raising=False)
        monkeypatch.delitem(sys.modules, "tabulate", raising=False)
        monkeypatch.setattr(sys, "meta_path", [_BlockTabulate(), *sys.meta_path])

        ctx = Context(cli, info_name="mmemoji")
        with pytest.raises(ModuleNotFoundError):
            cli.get_command(ctx, "list")
