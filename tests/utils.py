from contextlib import contextmanager
from unittest.mock import patch
from urllib.parse import urlparse

from mattermostdriver import Driver as Mattermost

API_URL = "http://localhost:8065/api/v4"
EMOJIS = {
    "emoji_1": {
        "path": "tests/emojis/emoji_1.png",
        "sha1": "c29a0aa47f58adf95dc9da261b602c5dca51dd3f",
    },
    "emoji_2": {
        "path": "tests/emojis/emoji_2.png",
        "sha1": "9c539fefceef37c97c189ec17a9699a71c912d00",
    },
    "emoji_3": {
        "path": "tests/emojis/emoji_3.png",
        "sha1": "86dc153688e8c0801576a3438263cfafa755b1e4",
    },
    "parentheses_spaced": {
        "path": "tests/emojis/parentheses (spaced).png",
        "sha1": "23d46167de0846dcf2f94d8635c68c3382e37f95",
    },
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


class EmojiReconciler:
    """Maintain state of custom emojis in Mattermost"""

    def __init__(self, emoji_names, user):
        self.user = user
        self.emoji_names = emoji_names
        self.mattermost = None
        self.authenticate()

    def authenticate(self):
        """Authenticate against the Mattermost server"""
        url = urlparse(API_URL)
        settings = {
            "scheme": url.scheme,
            "url": url.hostname,
            "port": url.port,
            "basepath": url.path,
            "login_id": USERS[self.user]["email"],
            "password": USERS[self.user]["password"],
        }

        self.mattermost = Mattermost(settings)
        self.mattermost.login()

    def create(self, name):
        """Create emojis using a specific user"""
        with open(EMOJIS[name]["path"], "rb") as image:
            return self.mattermost.emoji.create_custom_emoji(
                name, {"image": image}
            )

    def delete(self, emoji):
        """Delete emojis using a specific user"""
        self.mattermost.emoji.delete_custom_emoji(emoji["id"])

    def get_actual(self):
        """Get list of existing custom emojis on Mattermost"""
        emojis = []
        count, previous_count = 0, 0
        params = {"page": 0, "per_page": 200}
        while True:
            emojis += self.mattermost.emoji.get_emoji_list(params=params)
            count = len(emojis)
            if count - previous_count < 200:
                break
            params["page"] += 1
            previous_count = count
        return emojis

    def get_expected(self):
        """Return list of desired emojis"""
        return self.emoji_names

    def reconcile(self):
        """Make the expected emojis match the actual emojis in Mattermost"""
        actual_emojis = self.get_actual()
        expected_emojis = self.get_expected()
        emojis = []
        for emoji in actual_emojis:
            if emoji["name"] not in expected_emojis:
                self.delete(emoji)
            else:
                emojis.append(emoji)
        for name in expected_emojis:
            if name not in [e["name"] for e in actual_emojis]:
                emojis.append(self.create(name))
        return emojis

    def destroy(self):
        """Destroy all emojis on Mattermost"""
        for emoji in self.get_actual():
            self.delete(emoji)


@contextmanager
def emoji_inventory(*args, **kwargs):
    """
    Set up an inventory of emojis for the duration of a test, and then clean up
    """
    reconcilier = EmojiReconciler(*args, **kwargs)
    reconcilier.reconcile()
    yield
    reconcilier.destroy()


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
