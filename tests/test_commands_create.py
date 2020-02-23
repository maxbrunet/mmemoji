import json

from click.testing import CliRunner

from mmemoji.cli import cli

from .utils import EMOJIS, emoji_inventory, find_dict_in_list, user_env


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["create", "--help"])
    assert result.exit_code == 0


def test_create_emoji(cli_runner):
    # Setup
    emoji_name = "emoji_1"
    emoji_path = EMOJIS[emoji_name]["path"]
    user = "user-1"
    # Test
    with user_env(user), emoji_inventory([], user):
        result = cli_runner.invoke(cli, ["create", emoji_path, "-o", "json"])
    emoji_list = json.loads(result.stdout)
    emoji = find_dict_in_list(emoji_list, "name", emoji_name)
    assert result.exit_code == 0
    assert len(emoji_list) == 1
    assert emoji["name"] == emoji_name


def test_create_exiting_emoji(cli_runner):
    # Setup
    emoji_name = "emoji_1"
    emoji_path = EMOJIS[emoji_name]["path"]
    user = "user-1"
    # Test
    with user_env(user), emoji_inventory([emoji_name], user):
        result = cli_runner.invoke(cli, ["create", emoji_path, "-o", "json"])
    assert result.exit_code == 1
    error = result.stderr.split("\n")[-2]
    assert error == 'Error: Emoji "{}" exists'.format(emoji_name)


def test_force_create_emoji(cli_runner):
    # Setup
    emoji_name = "emoji_1"
    emoji_path = EMOJIS[emoji_name]["path"]
    user = "user-1"
    # Test
    with user_env(user), emoji_inventory([], user):
        result = cli_runner.invoke(
            cli, ["create", "--force", emoji_path, "-o", "json"]
        )
    emoji_list = json.loads(result.stdout)
    emoji = find_dict_in_list(emoji_list, "name", emoji_name)
    assert result.exit_code == 0
    assert len(emoji_list) == 1
    assert emoji["name"] == emoji_name


def test_force_create_existing_emoji(cli_runner):
    # Setup
    emoji_name = "emoji_1"
    emoji_path = EMOJIS[emoji_name]["path"]
    user = "user-1"
    # Test
    with user_env(user), emoji_inventory([emoji_name], user):
        result = cli_runner.invoke(
            cli, ["create", "--force", emoji_path, "-o", "json"]
        )
    emoji_list = json.loads(result.stdout)
    emoji = find_dict_in_list(emoji_list, "name", emoji_name)
    assert result.exit_code == 0
    assert len(emoji_list) == 1
    assert emoji["name"] == emoji_name


def test_no_clobber_create_emoji(cli_runner):
    # Setup
    emoji_name = "emoji_1"
    emoji_path = EMOJIS[emoji_name]["path"]
    user = "user-1"
    # Test
    with user_env(user), emoji_inventory([], user):
        result = cli_runner.invoke(
            cli, ["create", "--no-clobber", emoji_path, "-o", "json"]
        )
    emoji_list = json.loads(result.stdout)
    emoji = find_dict_in_list(emoji_list, "name", emoji_name)
    assert result.exit_code == 0
    assert len(emoji_list) == 1
    assert emoji["name"] == emoji_name


def test_no_clobber_create_existing_emoji(cli_runner):
    # Setup
    emoji_name = "emoji_1"
    emoji_path = EMOJIS[emoji_name]["path"]
    user = "user-1"
    # Test
    with user_env(user), emoji_inventory([emoji_name], user):
        result = cli_runner.invoke(
            cli, ["create", "--no-clobber", emoji_path, "-o", "json"]
        )
    assert result.exit_code == 0
    assert result.stdout == ""


def test_interactive_create_emoji(cli_runner):
    # Setup
    # 1st will not exist and will be created
    # 2nd will exist and will be overwritten
    # 3rd will exist and will not be overwritten
    user = "user-1"
    emoji_names = ["emoji_1", "emoji_2", "emoji_3"]
    emoji_paths = [EMOJIS[name]["path"] for name in emoji_names]
    # Test
    with user_env(user), emoji_inventory(emoji_names[1:], user):
        result = cli_runner.invoke(
            cli,
            ["create", "--interactive", "-o", "json"] + emoji_paths,
            input="yes\nno\n",
        )
    assert result.exit_code == 0
    # Output contains the invocation input as well
    emoji_list = json.loads(result.stdout.split("\n")[-2])
    emoji1 = find_dict_in_list(emoji_list, "name", emoji_names[0])
    emoji2 = find_dict_in_list(emoji_list, "name", emoji_names[1])
    assert len(emoji_list) == 2
    assert emoji1["name"] == emoji_names[0]
    assert emoji2["name"] == emoji_names[1]
