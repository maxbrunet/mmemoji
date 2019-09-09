import json

from click.testing import CliRunner

from mmemoji.cli import cli

from .utils import create_emojis, delete_emojis, find_dict_in_list, user_env


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "--help"])
    assert result.exit_code == 0


def test_search_emoji(cli_runner):
    # Setup
    user = "user-1"
    emoji_names = ["emoji_1", "emoji_2", "parentheses_spaced"]
    create_emojis(emoji_names, user)
    # Test
    with user_env(user):
        result = cli_runner.invoke(cli, ["search", "-o", "json", "space"])
    assert result.exit_code == 0
    emoji_list = json.loads(result.stdout)
    emoji = find_dict_in_list(emoji_list, "name", emoji_names[-1])
    assert len(emoji_list) == 1
    assert emoji["name"] == emoji_names[-1]
    # Teardown
    delete_emojis(emoji_names, user)


def test_search_prefix_only(cli_runner):
    # Setup
    user = "user-1"
    emoji_names = ["emoji_1", "emoji_2", "parentheses_spaced"]
    create_emojis(emoji_names, user)
    # Test
    with user_env(user):
        result = cli_runner.invoke(
            cli, ["search", "-o", "json", "--prefix-only", "paren"]
        )
    assert result.exit_code == 0
    emoji_list = json.loads(result.stdout)
    emoji = find_dict_in_list(emoji_list, "name", emoji_names[-1])
    assert len(emoji_list) == 1
    assert emoji["name"] == emoji_names[-1]
    # Teardown
    delete_emojis(emoji_names, user)


def test_search_emoji_non_matching_prefix_only(cli_runner):
    # Setup
    user = "user-1"
    emoji_names = ["emoji_1", "emoji_2", "parentheses_spaced"]
    create_emojis(emoji_names, user)
    # Test
    with user_env(user):
        result = cli_runner.invoke(
            cli, ["search", "-o", "json", "--prefix-only", "space"]
        )
    assert result.exit_code == 0
    assert result.stdout == ""
    # Teardown
    delete_emojis(emoji_names, user)
