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

    @staticmethod
    def list(mattermost, page=0, per_page=200, sort="name"):
        """List custom Emojis on Mattermost.

        Parameters
        ----------
        mattermost : :obj:`mattermostdriver.Driver`
            an instance of `mattermostdriver`_
        page: int
            The page to select.
        per_page: int
            The number of users per page.
        sort: string
            Either blank for no sorting or "name" to sort by emoji names.

        Returns
        -------
        :obj:`list` of `dict`
            Returns a list of Emojis
        """
        emojis = []
        count, previous_count = 0, 0
        params = {"page": page, "per_page": per_page, "sort": sort}
        while True:
            emojis += mattermost.emoji.get_emoji_list(params=params)
            count = len(emojis)
            if count - previous_count < per_page:
                break
            params["page"] += 1
            previous_count = count
        return emojis

    @staticmethod
    def search(mattermost, term, prefix_only=False):
        """Search custom Emojis on Mattermost.

        Parameters
        ----------
        mattermost : :obj:`mattermostdriver.Driver`
            an instance of `mattermostdriver`_
        term: str
            The term to match against the emoji name.
        prefix_only: bool
            Set to only search for names starting with the search term.

        Returns
        -------
        :obj:`list` of `dict`
            Returns a list of Emojis
        """
        return mattermost.emoji.search_custom_emoji(
            options={"term": term, "prefix_only": prefix_only}
        )
