import hashlib
import os
from collections.abc import Callable
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Any
from unittest.mock import _patch_dict

import pytest
from click.testing import CliRunner

from mmemoji.cli import cli


@pytest.mark.usefixtures("class_utils")
class TestDownload:
    cli_runner: CliRunner
    emoji_inventory: Callable[[list[str], str], AbstractContextManager[None]]
    get_emoji_sha256: Callable[[str], str]
    find_dict_in_list: Callable[
        [list[dict[str, Any]], str, Any], dict[str, Any] | None
    ]
    user_env: Callable[[str], _patch_dict]

    def test_help(self) -> None:
        result = self.cli_runner.invoke(cli, ["create", "--help"])
        assert result.exit_code == 0

    def test_download_emoji_to_directory(self, tmp_path: Path) -> None:
        # Setup
        destination = tmp_path
        emoji_name = "emoji_1"
        emoji_filename = f"{emoji_name}.png"
        emoji_sha256 = self.get_emoji_sha256(emoji_name)
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory([emoji_name], user):
            result = self.cli_runner.invoke(
                cli, ["download", emoji_name, str(destination)]
            )
        paths = result.stdout.strip().split("\n")
        assert result.exit_code == 0
        assert len(paths) == 1
        assert os.path.basename(paths[0]) == emoji_filename
        with (destination / emoji_filename).open("rb") as f:
            assert hashlib.sha256(f.read()).hexdigest() == emoji_sha256

    def test_download_emojis(self, tmp_path: Path) -> None:
        # Setup
        destination = tmp_path
        emoji_names = ["emoji_1", "emoji_2"]
        emoji_filenames = []
        emoji_sha256s = []
        for e in emoji_names:
            emoji_filenames.append(f"{e}.png")
            emoji_sha256s.append(self.get_emoji_sha256(e))
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory(emoji_names, user):
            result = self.cli_runner.invoke(
                cli, ["download", *emoji_names, str(destination)]
            )
        paths = result.stdout.strip().split("\n")
        assert result.exit_code == 0
        assert len(paths) == 2
        for i, path in enumerate(paths):
            assert os.path.basename(path) == emoji_filenames[i]
            with (destination / emoji_filenames[i]).open("rb") as f:
                assert hashlib.sha256(f.read()).hexdigest() == emoji_sha256s[i]

    def test_download_emoji_to_full_path(self, tmp_path: Path) -> None:
        # Setup
        destination = tmp_path / "my_emoji.img"
        emoji_name = "emoji_1"
        emoji_sha256 = self.get_emoji_sha256(emoji_name)
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory([emoji_name], user):
            result = self.cli_runner.invoke(
                cli, ["download", emoji_name, str(destination)]
            )
        paths = result.stdout.strip().split("\n")
        assert result.exit_code == 0
        assert len(paths) == 1
        with destination.open("rb") as f:
            assert hashlib.sha256(f.read()).hexdigest() == emoji_sha256

    def test_download_emoji_to_non_existing(self) -> None:
        # Setup
        destination = os.path.join("path", "that", "does", "not", "exists")
        emoji_name = "emoji_1"
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory([emoji_name], user):
            result = self.cli_runner.invoke(
                cli, ["download", emoji_name, str(destination)]
            )
        assert result.exit_code != 0
        assert not result.stdout
        assert (
            result.stderr
            == f"Error: {os.path.dirname(destination)}: Not a directory\n"
        )

    def test_download_to_non_writable(self, tmp_path: Path) -> None:
        # Setup
        destination = tmp_path
        os.chmod(destination, 0o440)
        emoji_name = "emoji_1"
        user = "user-1"
        # Test
        with self.user_env(user), self.emoji_inventory([emoji_name], user):
            result = self.cli_runner.invoke(
                cli, ["download", emoji_name, str(destination)]
            )
        assert result.exit_code != 0
        assert not result.stdout
        assert result.stderr == f"Error: {destination}: Permission denied\n"

    def test_no_clobber_download(self, tmp_path: Path) -> None:
        # Setup
        destination = tmp_path
        emoji_names = ["emoji_1", "emoji_2"]
        emoji_filenames = [f"{e}.png" for e in emoji_names]
        emoji_sha256 = self.get_emoji_sha256(emoji_names[1])
        user = "user-1"
        # Test
        Path(destination / emoji_filenames[0]).touch()
        with self.user_env(user), self.emoji_inventory(emoji_names, user):
            result = self.cli_runner.invoke(
                cli,
                ["download", "--no-clobber", *emoji_names, str(destination)],
            )
        paths = result.stdout.strip().split("\n")
        assert result.exit_code == 0
        assert len(paths) == 1
        assert os.path.basename(paths[0]) == emoji_filenames[1]
        assert os.stat(destination / emoji_filenames[0]).st_size == 0
        with (destination / emoji_filenames[1]).open("rb") as f:
            assert hashlib.sha256(f.read()).hexdigest() == emoji_sha256

    def test_force_download(self, tmp_path: Path) -> None:
        # Setup
        destination = tmp_path
        emoji_names = ["emoji_1", "emoji_2"]
        emoji_filenames = []
        emoji_sha256s = []
        for e in emoji_names:
            emoji_filenames.append(f"{e}.png")
            emoji_sha256s.append(self.get_emoji_sha256(e))
        user = "user-1"
        # Test
        Path(destination / emoji_filenames[0]).touch()
        with self.user_env(user), self.emoji_inventory(emoji_names, user):
            result = self.cli_runner.invoke(
                cli, ["download", "--force", *emoji_names, str(destination)]
            )
        paths = result.stdout.strip().split("\n")
        assert result.exit_code == 0
        assert len(paths) == 2
        for i, path in enumerate(paths):
            assert os.path.basename(path) == emoji_filenames[i]
            with (destination / emoji_filenames[i]).open("rb") as f:
                assert hashlib.sha256(f.read()).hexdigest() == emoji_sha256s[i]

    def test_interactive_download(self, tmp_path: Path) -> None:
        # Setup
        # 1st will not exist and will be downloaded
        # 2nd will exist and will be overwritten
        # 3rd will exist and will not be overwritten
        destination = tmp_path
        emoji_names = ["emoji_1", "emoji_2", "emoji_3"]
        emoji_filenames = []
        emoji_sha256s = []
        emoji_paths = []
        for e in emoji_names:
            emoji_filenames.append(f"{e}.png")
            emoji_sha256s.append(self.get_emoji_sha256(e))
            emoji_paths.append(Path(destination / e))
        user = "user-1"
        # Test
        for e in emoji_filenames[1:]:
            Path(destination / e).touch()
        with self.user_env(user), self.emoji_inventory(emoji_names, user):
            result = self.cli_runner.invoke(
                cli,
                ["download", "--interactive", *emoji_names, str(destination)],
                input="yes\nno\n",
            )
        # output is sliced to exclude input from it
        paths = result.stdout.strip().split("\n")[0::2]
        assert result.exit_code == 0
        assert len(paths) == 2
        assert os.stat(destination / emoji_filenames[2]).st_size == 0
        for i, path in enumerate(paths):
            assert os.path.basename(path) == emoji_filenames[i]
            with (destination / emoji_filenames[i]).open("rb") as f:
                assert hashlib.sha256(f.read()).hexdigest() == emoji_sha256s[i]
