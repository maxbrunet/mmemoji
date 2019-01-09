from mattermostdriver.exceptions import (
    InvalidOrMissingParameters,
    ResourceNotFound,
)


class EmojiNotFound(ResourceNotFound):
    """Raised when an Emoji is not found on the Mattermost server"""

    def __init__(self, emoji):
        super().__init__('Emoji "{}" does not exist'.format(emoji.name))


class EmojiAlreadyExists(InvalidOrMissingParameters):
    """Raised when an Emoji already exists on the Mattermost server"""

    def __init__(self, emoji):
        super().__init__('Emoji "{}" exists'.format(emoji.name))
