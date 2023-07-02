from importlib import metadata

from mmemoji.emoji import Emoji

__all__ = ["Emoji"]
__version__ = metadata.version(__name__)
__summary__ = metadata.metadata(__name__)["Summary"]
