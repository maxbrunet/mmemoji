from mmemoji import Emoji


def test_emoji_sanitize_simple_name() -> None:
    name = Emoji.sanitize_name("emoji_1")
    assert name == "emoji_1"


def test_emoji_sanitize_name_with_parentheses() -> None:
    name = Emoji.sanitize_name("{[(parentheses)]}")
    assert name == "parentheses"


def test_emoji_sanitize_name_with_spaces() -> None:
    name = Emoji.sanitize_name("spa a ace")
    assert name == "spa_a_ace"


def test_emoji_sanitize_name_with_accents() -> None:
    name = Emoji.sanitize_name("àéêöhelloĐıł")
    assert name == "aeeohelloDil"
