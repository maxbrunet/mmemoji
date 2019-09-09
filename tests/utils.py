from unittest.mock import patch
from urllib.parse import urlparse

from mattermostdriver import Driver as Mattermost

API_URL = "http://localhost:8065/api/v4"
EMOJIS = {
    "emoji_1": "tests/emojis/emoji_1.png",
    "emoji_2": "tests/emojis/emoji_2.png",
    "emoji_3": "tests/emojis/emoji_3.png",
    "parentheses_spaced": "tests/emojis/parentheses (spaced).png",
}
USERS = {
    "sysadmin": {
        "username": "sysadmin",
        "email": "sysadmin@sample.mattermost.com",
        "password": "Sys@dmin-sample1",
    },
    "user-1": {
        "username": "user-1",
        "email": "user-1@sample.mattermost.com",
        "password": "SampleUs@r-1",
    },
}


def find_dict_in_list(lst, key, value):
    """Find a dict by key name inside a list"""
    for dic in lst:
        if dic[key] == value:
            return dic
    return None


def user_env(user):
    """Patch env with user credentials"""
    return patch.dict(
        "os.environ",
        {
            "MM_URL": API_URL,
            "MM_LOGIN_ID": USERS[user]["email"],
            "MM_PASSWORD": USERS[user]["password"],
        },
    )


def authenticate(user):
    """Authenticate against the Mattermost server"""
    url = urlparse(API_URL)
    settings = {
        "scheme": url.scheme,
        "url": url.hostname,
        "port": url.port,
        "basepath": url.path,
        "login_id": USERS[user]["email"],
        "password": USERS[user]["password"],
    }

    mattermost = Mattermost(settings)
    mattermost.login()
    return mattermost


def create_emojis(emojis, user):
    """Create emojis using a specific user"""
    mattermost = authenticate(user)
    for name in emojis:
        with open(EMOJIS[name], "rb") as image:
            mattermost.emoji.create_custom_emoji(name, {"image": image})
    mattermost.logout()


def delete_emojis(emojis, user):
    """Delete emojis using a specific user"""
    mattermost = authenticate(user)
    for name in emojis:
        emoji = mattermost.emoji.get_custom_emoji_by_name(name)
        mattermost.emoji.delete_custom_emoji(emoji["id"])
    mattermost.logout()
