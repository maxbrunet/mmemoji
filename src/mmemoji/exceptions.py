from typing import TYPE_CHECKING

from mattermostautodriver.exceptions import (
    InvalidOrMissingParameters,
    ResourceNotFound,
)

if TYPE_CHECKING:
    from mmemoji import Emoji


class EmojiNotFound(ResourceNotFound):  # type: ignore[misc]
    """Raised when an Emoji is not found on the Mattermost server"""

    def __init__(self, emoji: "Emoji") -> None:
        super().__init__(
            message=f'Emoji "{emoji.name}" does not exist',
            error_id="",
            request_id="",
            is_oauth_error=False,
        )


class EmojiAlreadyExists(InvalidOrMissingParameters):  # type: ignore[misc]
    """Raised when an Emoji already exists on the Mattermost server"""

    def __init__(self, emoji: "Emoji") -> None:
        super().__init__(
            message=f'Emoji "{emoji.name}" exists',
            error_id="",
            request_id="",
            is_oauth_error=False,
        )
