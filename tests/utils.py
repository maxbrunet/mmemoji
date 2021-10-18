from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional, cast
from unittest.mock import _patch_dict, patch
from urllib.parse import urlparse

from mattermostdriver import Driver as Mattermost

API_URL = "http://localhost:8065/api/v4"
EMOJIS = {
    "emoji_1": {
        "path": "tests/emojis/emoji_1.png",
        "sha256": "30a8638bb79d7a99d1d8143f2679046bf7e495918fca770408011ba9579a86c7",  # noqa: E501
    },
    "emoji_2": {
        "path": "tests/emojis/emoji_2.png",
        "sha256": "725f66fba4cb6f60987f09b70d1fbd73b2f08fa4437841032103cc5300252056",  # noqa: E501
    },
    "emoji_3": {
        "path": "tests/emojis/emoji_3.png",
        "sha256": "03f4f45da7d0f8b4ee27d5961b3302b6707d1154cd2a928aeb16b107656c6a7a",  # noqa: E501
    },
    "parentheses_spaced": {
        "path": "tests/emojis/parentheses (spaced).png",
        "sha256": "195645113194074832ac56af71de520f1e2e87e52e4c8268b675832b91bab003",  # noqa: E501
    },
    "accentue": {
        "path": "tests/emojis/accentué.png",
        "sha256": "508c3f7dd47fdc0e879748cb0286e9de82d8945aab3a580c58a4a6682df6ab8f",  # noqa: E501
    },
}
USERS = {
    "sysadmin": {
        "username": "sysadmin",
        "email": "sysadmin@sample.mattermost.com",
        "password": "Sys@dmin-sample1",  # NOSONAR
    },
    "user-1": {
        "username": "user-1",
        "email": "user-1@sample.mattermost.com",
        "password": "SampleUs@r-1",  # NOSONAR
    },
}


class EmojiReconciler:
    """Maintain state of custom emojis in Mattermost"""

    def __init__(self, emoji_names: List[str], user: str) -> None:
        self.user = user
        self.emoji_names = emoji_names
        self.mattermost: Any = None
        self.authenticate()

    def authenticate(self) -> None:
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

    def create(self, name: str) -> Dict[str, Any]:
        """Create emojis using a specific user"""
        with open(EMOJIS[name]["path"], "rb") as image:
            return cast(
                Dict[str, Any],
                self.mattermost.emoji.create_custom_emoji(
                    name, {"image": image}
                ),
            )

    def delete(self, emoji: Dict[str, Any]) -> None:
        """Delete emojis using a specific user"""
        self.mattermost.emoji.delete_custom_emoji(emoji["id"])

    def get_actual(self) -> List[Dict[str, Any]]:
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

    def get_expected(self) -> List[str]:
        """Return list of desired emojis"""
        return self.emoji_names

    def reconcile(self) -> List[Dict[str, Any]]:
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

    def destroy(self) -> None:
        """Destroy all emojis on Mattermost"""
        for emoji in self.get_actual():
            self.delete(emoji)


@contextmanager
def emoji_inventory(emoji_names: List[str], user: str) -> Iterator[None]:
    """
    Set up an inventory of emojis for the duration of a test, and then clean up
    """
    reconcilier = EmojiReconciler(emoji_names, user)
    reconcilier.reconcile()
    yield
    reconcilier.destroy()


def find_dict_in_list(
    lst: List[Dict[str, Any]], key: str, value: Any
) -> Optional[Dict[str, Any]]:
    """Find a dict by key name inside a list"""
    for dic in lst:
        if dic[key] == value:
            return dic
    return None


def user_env(user: str) -> _patch_dict:
    """Patch env with user credentials"""
    return patch.dict(
        "os.environ",
        {
            "MM_URL": API_URL,
            "MM_LOGIN_ID": USERS[user]["email"],
            "MM_PASSWORD": USERS[user]["password"],
        },
    )
