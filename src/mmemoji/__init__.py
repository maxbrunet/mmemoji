import sys

from mmemoji.emoji import Emoji

# https://github.com/python/mypy/issues/1153
if sys.version_info[:2] >= (3, 8):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata


__all__ = ["Emoji"]
__version__ = importlib_metadata.version(__name__)
__summary__ = importlib_metadata.metadata(__name__)["Summary"]
