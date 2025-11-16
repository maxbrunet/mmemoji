from collections.abc import Callable
from typing import TypedDict
from urllib.parse import ParseResult, urlparse

import pytest

from mmemoji.decorators import EmojiContext


@pytest.mark.usefixtures("class_utils")
class TestDecorators:
    api_url: str
    get_user_username: Callable[[str], str]
    get_user_password: Callable[[str], str]

    def test_emojicontext_authenticate_password(self) -> None:
        observer_ctx = EmojiContext()
        ctx = EmojiContext()
        url = urlparse(self.api_url)
        username = self.get_user_username("user-1")
        password = self.get_user_password("user-1")

        class AuthnKwargs(TypedDict):
            url: ParseResult
            token: str
            login_id: str
            password: str
            mfa_token: str
            insecure: bool

        authn_kwargs = AuthnKwargs(
            url=url,
            token="",
            login_id=username,
            password=password,
            mfa_token="",
            insecure=True,
        )

        with observer_ctx.authenticate(**authn_kwargs):
            user = observer_ctx.mattermost.users.get_user_by_username(username)
            user_id = user["id"]
            sessions_before = observer_ctx.mattermost.users.get_sessions(
                user_id
            )
            with ctx.authenticate(**authn_kwargs):
                sessions = ctx.mattermost.users.get_sessions(user_id)
                assert len(sessions) == len(sessions_before) + 1
            sessions_after = observer_ctx.mattermost.users.get_sessions(
                user_id
            )
            assert len(sessions_after) == len(sessions_before)
