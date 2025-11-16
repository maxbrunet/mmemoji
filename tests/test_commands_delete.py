import json
from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any, cast
from unittest.mock import _patch_dict

import pytest
from click.testing import CliRunner

from mmemoji.cli import cli


@pytest.mark.usefixtures("class_utils")
class TestDelete:
    cli_runner: CliRunner
    emoji_inventory: Callable[[list[str], str], AbstractContextManager[None]]
    find_dict_in_list: Callable[
        [list[dict[str, Any]], str, Any], dict[str, Any] | None
    ]
    get_emoji_path: Callable[[str], str]
    user_env: Callable[[str], _patch_dict]

    def test_help(self) -> None:
        result = self.cli_runner.invoke(cli, ["delete", "--help"])
        assert result.exit_code == 0

    def test_delete_emoji(self) -> None:
        # Setup
        emoji_name = "emoji_1"
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory([emoji_name], user):
            result = self.cli_runner.invoke(
                cli, ["delete", emoji_name, "-o", "json"]
            )
        emoji_list = json.loads(result.stdout)
        emoji = cast(
            "dict[str, Any]",
            self.find_dict_in_list(emoji_list, "name", emoji_name),
        )
        assert result.exit_code == 0
        assert len(emoji_list) == 1
        assert emoji["name"] == emoji_name

    def test_delete_absent_emoji(self) -> None:
        # Setup
        emoji_name = "absent_emoji"
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory([], user):
            result = self.cli_runner.invoke(
                cli, ["delete", emoji_name, "-o", "json"]
            )
        assert result.exit_code == 1
        assert result.stdout == "\n"
        error = result.stderr.split("\n")[-2]
        assert error == f'Error: Emoji "{emoji_name}" does not exist'

    def test_force_delete_emoji(self) -> None:
        # Setup
        emoji_name = "emoji_1"
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory([emoji_name], user):
            result = self.cli_runner.invoke(
                cli, ["delete", "--force", emoji_name, "-o", "json"]
            )
        emoji_list = json.loads(result.stdout)
        emoji = cast(
            "dict[str, Any]",
            self.find_dict_in_list(emoji_list, "name", emoji_name),
        )
        assert result.exit_code == 0
        assert len(emoji_list) == 1
        assert emoji["name"] == emoji_name

    def test_force_delete_absent_emoji(self) -> None:
        # Setup
        emoji_name = "absent_emoji"
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory([], user):
            result = self.cli_runner.invoke(
                cli, ["delete", "--force", emoji_name, "-o", "json"]
            )
        assert result.exit_code == 0
        assert result.stdout == "\n"

    def test_interactive_delete_emoji(self) -> None:
        # Setup
        # 1st will be deleted
        # 2nd will not be deleted
        user = "user-1"
        emoji_names = ["emoji_1", "emoji_2"]
        emoji_paths = [self.get_emoji_path(name) for name in emoji_names]
        # Test
        with self.user_env(user), self.emoji_inventory(emoji_names, user):
            result = self.cli_runner.invoke(
                cli,
                ["delete", "--interactive", "-o", "json", *emoji_paths],
                input="yes\nno\n",
            )
        assert result.exit_code == 0
        # Output contains the invocation input as well
        emoji_list = json.loads("\n".join(result.stdout.split("\n")[3:]))
        assert len(emoji_list) == 1
        emoji1 = cast(
            "dict[str, Any]",
            self.find_dict_in_list(emoji_list, "name", emoji_names[0]),
        )
        assert emoji1["name"] == emoji_names[0]
