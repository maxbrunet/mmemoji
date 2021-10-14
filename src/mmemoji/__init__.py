__all__ = ["Emoji"]
from mmemoji.emoji import Emoji

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)
__summary__ = importlib_metadata.metadata(__name__)["Summary"]
