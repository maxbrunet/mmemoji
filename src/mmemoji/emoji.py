"""Wrapper for Mattermost API ``/emoji`` Endpoint.

This wrapper is built around ``python-mattermostdriver``_

.. _python-mattermostdriver:
    https://vaelor.github.io/python-mattermost-driver/
"""

import re
from os.path import basename

from mattermostdriver.exceptions import ResourceNotFound

from mmemoji.exceptions import EmojiAlreadyExists, EmojiNotFound


class Emoji:
    """Interact with Mattermost custom Emojis."""

    def __init__(self, mattermost, name):
        """Init Emoji class with a Mattermost client instance and an Emoji name.

        Parameters
        ----------
        mattermost : :obj:`mattermostdriver.Driver`
            an instance of `mattermostdriver`_
        name : str
            an Emoji name. It can be a file path,
            the filename will be automatically extracted and sanitized
        """
        self._mm = mattermost
        self._name = self.sanitize_name(name)
        self._emoji = {}

    @staticmethod
    def sanitize_name(filepath):
        """Extract and sanitize an Emoji name from a file path.

        Parameters
        ----------
        filepath : str
            Emoji file path (e.g. ``/path/to/emoji (1).gif``)

        Returns
        -------
        str
            Emoji name (e.g. ``emoji_1``)
        """
        # Extract filename without extension
        name = basename(filepath).split(".")[0]
        # Remove parentheses
        name = re.sub(r"[()[\]{}]", "", name)
        # Replace forbidden characters by underscores
        name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
        return name

    def _get_from_mattermost(self):
        """Retrieve custom Emoji information from Mattermost."""
        try:
            self._emoji = self._mm.emoji.get_custom_emoji_by_name(self.name)
            return True
        except ResourceNotFound:
            self._emoji = {}
            return False

    @property
    def emoji(self):
        """:obj:`dict` of (str: str): Gets Emoji information."""
        if not self._emoji:
            self._get_from_mattermost()
        return self._emoji

    @property
    def name(self):
        """str: Get Emoji name."""
        return self._name

    def create(self, image, force=False, no_clobber=False):
        """Create a custom Emoji on Mattermost.

        Parameters
        ----------
        image : :obj:`file`
            an image to upload
        force: bool
            delete Emoji if it already exits
            (ignored if ``no_clobber is ``True``)
        no_clobber: bool
            do nothing if Emoji already exits

        Returns
        -------
        bool
            Returns ``True`` if Emoji was created

        Raises
        ------
        EmojiAlreadyExists
            If nor ``no_clobber`` or ``force`` were ``True``
        """
        if self.emoji:
            if no_clobber:
                return False
            elif force:
                self.delete()
            else:
                raise EmojiAlreadyExists(self)

        self._emoji = self._mm.emoji.create_custom_emoji(
            emoji_name=self._name, files={"image": image}
        )
        return True

    def delete(self, force=False):
        """Delete a custom Emoji on Mattermost.

        Parameters
        ----------
        force: bool
            Ignore non-existent Emoji

        Returns
        -------
        bool
            Returns ``True`` if Emoji was deleted

        Raises
        ------
        EmojiNotFound
            If Emoji does not exist and ``force`` was not ``True``
        """
        if not self.emoji and force:
            return False

        if self.emoji:
            self._mm.emoji.delete_custom_emoji(self.emoji.get("id", ""))
            return True
        else:
            raise EmojiNotFound(self)
