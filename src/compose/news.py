# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load news."""

import datetime
import re
from collections import UserList, UserString
from urllib import request
from urllib.error import URLError

from pydantic import TypeAdapter, ValidationError
from pydantic_utils import ReachableUrlList


class News(UserString):
    """Project news."""

    @property
    def title(self) -> str:
        """
        Get title from Markdown.

        Returns:
            str: title.

        Raises:
            ValueError: If the title cannot be parsed from the Markdown.
        """
        try:
            return re.search('^## (.+)', self.data).group(1).strip()
        except (re.error, TypeError, IndexError) as title_error:
            raise ValueError('Failed to parse title:\n{0}'.format(title_error))

    @property
    def date(self) -> datetime.date:
        """
        Get date from Markdown.

        Returns:
            datetime.date: date.

        Raises:
            ValueError: If the date cannot be parsed from the Markdown.
        """
        try:
            date = re.search(
                r'^\d{4}-\d{2}-\d{2}', self.data, re.MULTILINE,
            ).group(0)
        except (re.error, TypeError, IndexError) as error:
            raise ValueError('Failed to fetch date:\n{0}'.format(error))
        return datetime.date.fromisoformat(date)

    @property
    def images(self) -> list[str]:
        """
        Get images from Markdown.

        Returns:
            list[str]: images.

        Raises:
            ValueError: If the images cannot be parsed from the Markdown.
        """
        try:
            images = re.findall(r'!\[.*?\]\((.*?)\)', self.data)
        except re.error as error:
            raise ValueError('Failed to parse images:\n{0}'.format(error))
        ta = TypeAdapter(ReachableUrlList)
        try:
            ta.validate_python(images)
        except ValidationError as url_error:
            raise ValueError(
                'Failed to validate images:\n{0}'.format(url_error),
            )
        return images

    @property
    def description(self) -> str:
        """
        Get description from Markdown.

        Returns:
            str: description.

        Raises:
            ValueError: If the description cannot be parsed from the Markdown.
        """
        try:
            description = re.search(
                r'\d{4}-\d{2}-\d{2}(.*)', self.data, re.DOTALL,
            ).group(1)
        except (re.error, TypeError, IndexError) as description_error:
            raise ValueError(
                'Failed to parse description:\n{0}'.format(description_error),
            )
        try:
            description = re.sub(
                r'!\[.*?\]\(.*?\)', '', description, flags=re.DOTALL,
            )
        except (re.error, TypeError) as cleanup_error:
            raise ValueError(
                'Failed to cleanup description:\n{0}'.format(cleanup_error),
            )
        return description.strip()


class NewsList(UserList):
    """Project news list."""

    @classmethod
    def from_url(cls, url: str):
        """
        Load news list from a URL.

        Parameters:
            url: News list URL.

        Returns:
            NewsList object.

        Raises:
            ValueError: if loading the news list fails.
        """
        try:
            with request.urlopen(url, timeout=5) as res:  # noqa: S310
                return cls.from_md(res.read().decode('utf-8'))
        except (URLError, ValueError, TimeoutError) as urlopen_error:
            raise ValueError(
                "Failed to load news from '{0}':\n{1}".format(
                    url, urlopen_error,
                ),
            )

    @classmethod
    def from_md(cls, md: str):
        """
        Load news list from Markdown.

        Parameters:
            md: Markdown news list.

        Returns:
            NewsList object.

        Raises:
            ValueError: if loading the news list fails.
        """
        try:
            matches = re.findall(r'(## .+?)(?=\n## |$)', md, re.DOTALL)
        except (re.error, TypeError) as re_error:
            raise ValueError(
                'Failed to process Markdown:\n{0}'.format(re_error),
            )
        news_list = []
        for match in matches:
            news_list.append(News(match.strip()))
        return cls(news_list)
