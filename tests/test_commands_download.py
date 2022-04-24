import hashlib
import os
from pathlib import Path

from click.testing import CliRunner

from mmemoji.cli import cli

from .utils import EMOJIS, emoji_inventory, user_env

EMOJI_FILENAME_FORMAT = "{}.png"


def test_help(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(cli, ["create", "--help"])
    assert result.exit_code == 0


def test_download_emoji_to_directory(
    cli_runner: CliRunner, tmp_path: Path
) -> None:
    # Setup
    destination = tmp_path
    emoji_name = "emoji_1"
    emoji_filename = EMOJI_FILENAME_FORMAT.format(emoji_name)
    emoji_sha256 = EMOJIS[emoji_name]["sha256"]
    user = "user-1"
    # Test
    with user_env(user), emoji_inventory([emoji_name], user):
        result = cli_runner.invoke(
            cli, ["download", emoji_name, str(destination)]
        )
    paths = result.stdout.strip().split("\n")
    assert result.exit_code == 0
    assert len(paths) == 1
    assert os.path.basename(paths[0]) == emoji_filename
    with (destination / emoji_filename).open("rb") as f:
        assert hashlib.sha256(f.read()).hexdigest() == emoji_sha256


def test_download_emojis(cli_runner: CliRunner, tmp_path: Path) -> None:
    # Setup
    destination = tmp_path
    emoji_names = ["emoji_1", "emoji_2"]
    emoji_filenames = []
    emoji_sha256s = []
    for e in emoji_names:
        emoji_filenames.append(EMOJI_FILENAME_FORMAT.format(e))
        emoji_sha256s.append(EMOJIS[e]["sha256"])
    user = "user-1"
    # Test
    with user_env(user), emoji_inventory(emoji_names, user):
        result = cli_runner.invoke(
            cli, ["download"] + emoji_names + [str(destination)]
        )
    paths = result.stdout.strip().split("\n")
    assert result.exit_code == 0
    assert len(paths) == 2
    for i, path in enumerate(paths):
        assert os.path.basename(path) == emoji_filenames[i]
        with (destination / emoji_filenames[i]).open("rb") as f:
            assert hashlib.sha256(f.read()).hexdigest() == emoji_sha256s[i]


def test_download_emoji_to_full_path(
    cli_runner: CliRunner, tmp_path: Path
) -> None:
    # Setup
    destination = tmp_path / "my_emoji.img"
    emoji_name = "emoji_1"
    emoji_sha256 = EMOJIS[emoji_name]["sha256"]
    user = "user-1"
    # Test
    with user_env(user), emoji_inventory([emoji_name], user):
        result = cli_runner.invoke(
            cli, ["download", emoji_name, str(destination)]
        )
    paths = result.stdout.strip().split("\n")
    assert result.exit_code == 0
    assert len(paths) == 1
    with destination.open("rb") as f:
        assert hashlib.sha256(f.read()).hexdigest() == emoji_sha256


def test_download_emoji_to_non_existing(cli_runner: CliRunner) -> None:
    # Setup
    destination = os.path.join("path", "that", "does", "not", "exists")
    emoji_name = "emoji_1"
    user = "user-1"
    # Test
    with user_env(user), emoji_inventory([emoji_name], user):
        result = cli_runner.invoke(
            cli, ["download", emoji_name, str(destination)]
        )
    assert result.exit_code != 0
    assert not result.stdout
    assert result.stderr == "Error: {}: Not a directory\n".format(
        os.path.dirname(destination)
    )


def test_download_to_non_writable(
    cli_runner: CliRunner, tmp_path: Path
) -> None:
    # Setup
    destination = tmp_path
    os.chmod(destination, 0o440)
    emoji_name = "emoji_1"
    user = "user-1"
    # Test
    with user_env(user), emoji_inventory([emoji_name], user):
        result = cli_runner.invoke(
            cli, ["download", emoji_name, str(destination)]
        )
    print(result.stderr_bytes)
    assert result.exit_code != 0
    assert not result.stdout
    assert result.stderr == "Error: {}: Permission denied\n".format(
        destination
    )


def test_no_clobber_download(cli_runner: CliRunner, tmp_path: Path) -> None:
    # Setup
    destination = tmp_path
    emoji_names = ["emoji_1", "emoji_2"]
    emoji_filenames = [EMOJI_FILENAME_FORMAT.format(e) for e in emoji_names]
    emoji_sha256 = EMOJIS[emoji_names[1]]["sha256"]
    user = "user-1"
    # Test
    Path(destination / emoji_filenames[0]).touch()
    with user_env(user), emoji_inventory(emoji_names, user):
        result = cli_runner.invoke(
            cli,
            ["download", "--no-clobber"] + emoji_names + [str(destination)],
        )
    paths = result.stdout.strip().split("\n")
    assert result.exit_code == 0
    assert len(paths) == 1
    assert os.path.basename(paths[0]) == emoji_filenames[1]
    assert os.stat(destination / emoji_filenames[0]).st_size == 0
    with (destination / emoji_filenames[1]).open("rb") as f:
        assert hashlib.sha256(f.read()).hexdigest() == emoji_sha256


def test_force_download(cli_runner: CliRunner, tmp_path: Path) -> None:
    # Setup
    destination = tmp_path
    emoji_names = ["emoji_1", "emoji_2"]
    emoji_filenames = []
    emoji_sha256s = []
    for e in emoji_names:
        emoji_filenames.append(EMOJI_FILENAME_FORMAT.format(e))
        emoji_sha256s.append(EMOJIS[e]["sha256"])
    user = "user-1"
    # Test
    Path(destination / emoji_filenames[0]).touch()
    with user_env(user), emoji_inventory(emoji_names, user):
        result = cli_runner.invoke(
            cli, ["download", "--force"] + emoji_names + [str(destination)]
        )
    paths = result.stdout.strip().split("\n")
    assert result.exit_code == 0
    assert len(paths) == 2
    for i, path in enumerate(paths):
        assert os.path.basename(path) == emoji_filenames[i]
        with (destination / emoji_filenames[i]).open("rb") as f:
            assert hashlib.sha256(f.read()).hexdigest() == emoji_sha256s[i]


def test_interactive_download(cli_runner: CliRunner, tmp_path: Path) -> None:
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
        emoji_filenames.append(EMOJI_FILENAME_FORMAT.format(e))
        emoji_sha256s.append(EMOJIS[e]["sha256"])
        emoji_paths.append(Path(destination / e))
    user = "user-1"
    # Test
    for e in emoji_filenames[1:]:
        Path(destination / e).touch()
    with user_env(user), emoji_inventory(emoji_names, user):
        result = cli_runner.invoke(
            cli,
            ["download", "--interactive"] + emoji_names + [str(destination)],
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
