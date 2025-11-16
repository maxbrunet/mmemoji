import json
from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any, cast
from unittest.mock import _patch_dict

import pytest
from click.testing import CliRunner

from mmemoji.cli import cli


@pytest.mark.usefixtures("class_utils")
class TestSearch:
    cli_runner: CliRunner
    emoji_inventory: Callable[[list[str], str], AbstractContextManager[None]]
    find_dict_in_list: Callable[
        [list[dict[str, Any]], str, Any], dict[str, Any] | None
    ]
    user_env: Callable[[str], _patch_dict]

    def test_help(self) -> None:
        result = self.cli_runner.invoke(cli, ["search", "--help"])
        assert result.exit_code == 0

    def test_search_emoji(self) -> None:
        # Setup
        user = "user-1"
        emoji_names = ["emoji_1", "emoji_2", "parentheses_spaced"]
        # Test
        with self.user_env(user), self.emoji_inventory(emoji_names, user):
            result = self.cli_runner.invoke(
                cli, ["search", "-o", "json", "space"]
            )
        assert result.exit_code == 0
        emoji_list = json.loads(result.stdout)
        emoji = cast(
            "dict[str, Any]",
            self.find_dict_in_list(emoji_list, "name", emoji_names[-1]),
        )
        assert len(emoji_list) == 1
        assert emoji["name"] == emoji_names[-1]

    def test_search_prefix_only(self) -> None:
        # Setup
        user = "user-1"
        emoji_names = ["emoji_1", "emoji_2", "parentheses_spaced"]
        # Test
        with self.user_env(user), self.emoji_inventory(emoji_names, user):
            result = self.cli_runner.invoke(
                cli, ["search", "-o", "json", "--prefix-only", "paren"]
            )
        assert result.exit_code == 0
        emoji_list = json.loads(result.stdout)
        emoji = cast(
            "dict[str, Any]",
            self.find_dict_in_list(emoji_list, "name", emoji_names[-1]),
        )
        assert len(emoji_list) == 1
        assert emoji["name"] == emoji_names[-1]

    def test_search_emoji_non_matching_prefix_only(self) -> None:
        # Setup
        user = "user-1"
        emoji_names = ["emoji_1", "emoji_2", "parentheses_spaced"]
        # Test
        with self.user_env(user), self.emoji_inventory(emoji_names, user):
            result = self.cli_runner.invoke(
                cli, ["search", "-o", "json", "--prefix-only", "space"]
            )
        assert result.exit_code == 0
        assert result.stdout == ""
