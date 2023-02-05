from typing import TYPE_CHECKING

from mattermostdriver.exceptions import (
    InvalidOrMissingParameters,
    ResourceNotFound,
)

if TYPE_CHECKING:
    from mmemoji import Emoji


class EmojiNotFound(ResourceNotFound):  # type: ignore
    """Raised when an Emoji is not found on the Mattermost server"""

    def __init__(self, emoji: "Emoji") -> None:
        super().__init__(f'Emoji "{emoji.name}" does not exist')


class EmojiAlreadyExists(InvalidOrMissingParameters):  # type: ignore
    """Raised when an Emoji already exists on the Mattermost server"""

    def __init__(self, emoji: "Emoji") -> None:
        super().__init__(f'Emoji "{emoji.name}" exists')
