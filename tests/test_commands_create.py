import json
from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any, cast
from unittest.mock import _patch_dict

import pytest
from click.testing import CliRunner

from mmemoji.cli import cli


@pytest.mark.usefixtures("class_utils")
class TestCreate:
    cli_runner: CliRunner
    emoji_inventory: Callable[[list[str], str], AbstractContextManager[None]]
    get_emoji_path: Callable[[str], str]
    find_dict_in_list: Callable[
        [list[dict[str, Any]], str, Any], dict[str, Any] | None
    ]
    user_env: Callable[[str], _patch_dict]

    def test_help(self) -> None:
        result = self.cli_runner.invoke(cli, ["create", "--help"])
        assert result.exit_code == 0

    def test_create_emoji(self) -> None:
        # Setup
        emoji_name = "emoji_1"
        emoji_path = self.get_emoji_path(emoji_name)
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory([], user):
            result = self.cli_runner.invoke(
                cli, ["create", emoji_path, "-o", "json"]
            )
        emoji_list = json.loads(result.stdout)
        emoji = cast(
            "dict[str, Any]",
            self.find_dict_in_list(emoji_list, "name", emoji_name),
        )
        assert result.exit_code == 0
        assert len(emoji_list) == 1
        assert emoji["name"] == emoji_name

    def test_create_exiting_emoji(self) -> None:
        # Setup
        emoji_name = "emoji_1"
        emoji_path = self.get_emoji_path(emoji_name)
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory([emoji_name], user):
            result = self.cli_runner.invoke(
                cli, ["create", emoji_path, "-o", "json"]
            )
        assert result.exit_code == 1
        error = result.stderr.split("\n")[-2]
        assert error == f'Error: Emoji "{emoji_name}" exists'

    def test_create_exiting_system_emoji(self) -> None:
        # Setup
        emoji_name = "100"
        emoji_path = self.get_emoji_path(emoji_name)
        user = "user-1"
        # Test
        with self.user_env(user):
            result = self.cli_runner.invoke(
                cli, ["create", emoji_path, "-o", "json"]
            )
        assert result.exit_code == 1
        error = result.stderr.split("\n")[-2]
        assert (
            error
            == f'Error: Emoji "{emoji_name}" conflicts with existing system emoji'  # noqa: E501
        )

    def test_force_create_emoji(self) -> None:
        # Setup
        emoji_name = "emoji_1"
        emoji_path = self.get_emoji_path(emoji_name)
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory([], user):
            result = self.cli_runner.invoke(
                cli, ["create", "--force", emoji_path, "-o", "json"]
            )
        emoji_list = json.loads(result.stdout)
        emoji = cast(
            "dict[str, Any]",
            self.find_dict_in_list(emoji_list, "name", emoji_name),
        )
        assert result.exit_code == 0
        assert len(emoji_list) == 1
        assert emoji["name"] == emoji_name

    def test_force_create_existing_emoji(self) -> None:
        # Setup
        emoji_name = "emoji_1"
        emoji_path = self.get_emoji_path(emoji_name)
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory([emoji_name], user):
            result = self.cli_runner.invoke(
                cli, ["create", "--force", emoji_path, "-o", "json"]
            )
        emoji_list = json.loads(result.stdout)
        emoji = cast(
            "dict[str, Any]",
            self.find_dict_in_list(emoji_list, "name", emoji_name),
        )
        assert result.exit_code == 0
        assert len(emoji_list) == 1
        assert emoji["name"] == emoji_name

    def test_no_clobber_create_emoji(self) -> None:
        # Setup
        emoji_name = "emoji_1"
        emoji_path = self.get_emoji_path(emoji_name)
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory([], user):
            result = self.cli_runner.invoke(
                cli, ["create", "--no-clobber", emoji_path, "-o", "json"]
            )
        emoji_list = json.loads(result.stdout)
        emoji = cast(
            "dict[str, Any]",
            self.find_dict_in_list(emoji_list, "name", emoji_name),
        )
        assert result.exit_code == 0
        assert len(emoji_list) == 1
        assert emoji["name"] == emoji_name

    def test_no_clobber_create_existing_emoji(self) -> None:
        # Setup
        emoji_name = "emoji_1"
        emoji_path = self.get_emoji_path(emoji_name)
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory([emoji_name], user):
            result = self.cli_runner.invoke(
                cli, ["create", "--no-clobber", emoji_path, "-o", "json"]
            )
        assert result.exit_code == 0
        assert result.stdout == "\n"

    def test_create_no_clobber_exiting_system_emoji(self) -> None:
        # Setup
        emoji_name = "100"
        emoji_path = self.get_emoji_path(emoji_name)
        user = "user-1"
        # Test
        with self.user_env(user):
            result = self.cli_runner.invoke(
                cli, ["create", "--no-clobber", emoji_path, "-o", "json"]
            )
        assert result.exit_code == 0
        assert result.stdout == "\n"

    def test_interactive_create_emoji(self) -> None:
        # Setup
        # 1st will not exist and will be created
        # 2nd will exist and will be overwritten
        # 3rd will exist and will not be overwritten
        user = "user-1"
        emoji_names = ["emoji_1", "emoji_2", "emoji_3"]
        emoji_paths = [self.get_emoji_path(name) for name in emoji_names]
        # Test
        with self.user_env(user), self.emoji_inventory(emoji_names[1:], user):
            result = self.cli_runner.invoke(
                cli,
                ["create", "--interactive", "-o", "json", *emoji_paths],
                input="yes\nno\n",
            )
        assert result.exit_code == 0
        # Output contains the invocation input as well
        emoji_list = json.loads("\n".join(result.stdout.split("\n")[3:]))
        emoji1 = cast(
            "dict[str, Any]",
            self.find_dict_in_list(emoji_list, "name", emoji_names[0]),
        )
        emoji2 = cast(
            "dict[str, Any]",
            self.find_dict_in_list(emoji_list, "name", emoji_names[1]),
        )
        assert len(emoji_list) == 2
        assert emoji1["name"] == emoji_names[0]
        assert emoji2["name"] == emoji_names[1]
