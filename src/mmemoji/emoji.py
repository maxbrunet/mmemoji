"""Wrapper for Mattermost API ``/emoji`` Endpoint.

This wrapper is built around ``python-mattermostdriver``_

.. _python-mattermostdriver:
    https://vaelor.github.io/python-mattermost-driver/
"""

import re
from os.path import basename
from typing import IO, Any, Dict, List, cast

from mattermostdriver.exceptions import ResourceNotFound
from unidecode import unidecode

from mmemoji.exceptions import EmojiAlreadyExists, EmojiNotFound


class Emoji:
    """Interact with Mattermost custom Emojis."""

    def __init__(self, mattermost: Any, name: str) -> None:
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
        self._metadata: Dict[str, Any] = {}

    @staticmethod
    def sanitize_name(filepath: str) -> str:
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
        # Transliterate Unicode to ASCII (remove accents)
        name = unidecode(name)
        # Remove parentheses
        name = re.sub(r"[()[\]{}]", "", name)
        # Replace forbidden characters by underscores
        name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
        return name

    def _get_metadata_from_mattermost(self) -> bool:
        """Retrieve custom Emoji metadata from Mattermost."""
        try:
            self._metadata = self._mm.emoji.get_custom_emoji_by_name(self.name)
            return True
        except ResourceNotFound:
            self._metadata = {}
            return False

    @property
    def metadata(self) -> Dict[str, Any]:
        """:obj:`dict` of (str: Any): Gets Emoji metadata."""
        if not self._metadata:
            self._get_metadata_from_mattermost()
        return self._metadata

    @property
    def name(self) -> str:
        """str: Get Emoji name."""
        return self._name

    def create(
        self, image: IO[bytes], force: bool = False, no_clobber: bool = False
    ) -> bool:
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
        if self.metadata:
            if no_clobber:
                return False
            elif force:
                self.delete()
            else:
                raise EmojiAlreadyExists(self)

        self._metadata = self._mm.emoji.create_custom_emoji(
            emoji_name=self._name, files={"image": image}
        )
        return True

    def delete(self, force: bool = False) -> bool:
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
        if not self.metadata and force:
            return False

        if self.metadata:
            self._mm.emoji.delete_custom_emoji(self.metadata.get("id", ""))
            return True
        else:
            raise EmojiNotFound(self)

    @staticmethod
    def list(
        mattermost: Any, page: int = 0, per_page: int = 200, sort: str = "name"
    ) -> List[Dict[str, Any]]:
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
            Returns a list of Emoji metadata
        """
        metadata_list = []
        count, previous_count = 0, 0
        params = cast(
            Dict[str, Any],
            {"page": page, "per_page": per_page, "sort": sort},
        )
        while True:
            metadata_list += mattermost.emoji.get_emoji_list(params=params)
            count = len(metadata_list)
            if count - previous_count < per_page:
                break
            # https://github.com/python/mypy/issues/3816
            params["page"] += 1
            previous_count = count
        return metadata_list

    @staticmethod
    def search(
        mattermost: Any, term: str, prefix_only: bool = False
    ) -> List[Dict[str, Any]]:
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
            Returns a list of Emoji metadata
        """
        return cast(
            List[Dict[str, Any]],
            mattermost.emoji.search_custom_emoji(
                options={"term": term, "prefix_only": prefix_only}
            ),
        )

    def download(self) -> bytes:
        """Download a custom Emoji from Mattermost.

        Returns
        -------
        bytes
            Returns Emoji image

        Raises
        ------
        EmojiNotFound
            If Emoji does not exist
        """
        if self.metadata and "id" in self.metadata:
            return cast(
                bytes,
                self._mm.emoji.get_custom_emoji_image(
                    self.metadata["id"]
                ).content,
            )
        raise EmojiNotFound(self)
