import json
from typing import Any, cast

from click.testing import CliRunner

from mmemoji.cli import cli

from .utils import emoji_inventory, find_dict_in_list, user_env


def test_help(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(cli, ["search", "--help"])
    assert result.exit_code == 0


def test_search_emoji(cli_runner: CliRunner) -> None:
    # Setup
    user = "user-1"
    emoji_names = ["emoji_1", "emoji_2", "parentheses_spaced"]
    # Test
    with user_env(user), emoji_inventory(emoji_names, user):
        result = cli_runner.invoke(cli, ["search", "-o", "json", "space"])
    assert result.exit_code == 0
    emoji_list = json.loads(result.stdout)
    emoji = cast(
        "dict[str, Any]",
        find_dict_in_list(emoji_list, "name", emoji_names[-1]),
    )
    assert len(emoji_list) == 1
    assert emoji["name"] == emoji_names[-1]


def test_search_prefix_only(cli_runner: CliRunner) -> None:
    # Setup
    user = "user-1"
    emoji_names = ["emoji_1", "emoji_2", "parentheses_spaced"]
    # Test
    with user_env(user), emoji_inventory(emoji_names, user):
        result = cli_runner.invoke(
            cli, ["search", "-o", "json", "--prefix-only", "paren"]
        )
    assert result.exit_code == 0
    emoji_list = json.loads(result.stdout)
    emoji = cast(
        "dict[str, Any]",
        find_dict_in_list(emoji_list, "name", emoji_names[-1]),
    )
    assert len(emoji_list) == 1
    assert emoji["name"] == emoji_names[-1]


def test_search_emoji_non_matching_prefix_only(cli_runner: CliRunner) -> None:
    # Setup
    user = "user-1"
    emoji_names = ["emoji_1", "emoji_2", "parentheses_spaced"]
    # Test
    with user_env(user), emoji_inventory(emoji_names, user):
        result = cli_runner.invoke(
            cli, ["search", "-o", "json", "--prefix-only", "space"]
        )
    assert result.exit_code == 0
    assert result.stdout == ""
