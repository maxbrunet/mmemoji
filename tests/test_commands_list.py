import json

from click.testing import CliRunner

from mmemoji.cli import cli

from .utils import emoji_inventory, find_dict_in_list, user_env


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["list", "--help"])
    assert result.exit_code == 0


def test_list_emoji(cli_runner):
    # Setup
    user = "user-1"
    emoji_names = ["emoji_1", "emoji_2", "emoji_3"]
    # Test
    with user_env(user), emoji_inventory(emoji_names, user):
        result = cli_runner.invoke(cli, ["list", "-o", "json"])
    assert result.exit_code == 0
    emoji_list = json.loads(result.stdout)
    emoji1 = find_dict_in_list(emoji_list, "name", emoji_names[0])
    emoji2 = find_dict_in_list(emoji_list, "name", emoji_names[1])
    emoji3 = find_dict_in_list(emoji_list, "name", emoji_names[2])
    assert len(emoji_list) == len(emoji_names)
    assert emoji1["name"] == emoji_names[0]
    assert emoji2["name"] == emoji_names[1]
    assert emoji3["name"] == emoji_names[2]
