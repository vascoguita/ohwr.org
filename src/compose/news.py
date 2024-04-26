# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load news."""

import datetime
import re
from collections import UserList, UserString
from urllib import request
from urllib.error import URLError

from pydantic import HttpUrl, computed_field, validate_call
from pydantic_utils import AnnotatedStr


class News(UserString):
    """Project news."""
    
    @computed_field
    def title(self) -> str:
        """
        Retrieve the title from the news Markdown.

        Returns:
            str: title.

        Raises:
            ValueError: If the title cannot be parsed from the Markdown.
        """
        try:
            return re.search('^## (.+)', self.data).group(1)
        except (re.error, TypeError, IndexError) as title_error:
            raise ValueError('Failed to parse title:\n{0}'.format(title_error))

    @computed_field
    def date(self) -> datetime.date:
        try:
            date = re.search(
                r'^\d{4}-\d{2}-\d{2}', self.data, re.MULTILINE,
            ).group(0)
        except (re.error, TypeError, IndexError) as error:
            raise ValueError('Failed to fetch date:\n{0}'.format(error))
        return datetime.date.fromisoformat(date)

    @computed_field
    def images(self) -> list[str]:
        """
        Retrieve the images from the news Markdown.

        Returns:
            list[str]: images.

        Raises:
            ValueError: If the images cannot be parsed from the Markdown.
        """
        try:
            return re.findall(r'!\[.*?\]\((.*?)\)', self.data)
        except (re.error, IndexError) as error:
            raise ValueError('Failed to parse images:\n{0}'.format(error))

    @computed_field
    def description(self) -> str:
        """
        Retrieve the description from the news Markdown.

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
            return re.sub(r'!\[.*?\]\(.*?\)', '', description, flags=re.DOTALL)
        except (re.error, TypeError) as cleanup_error:
            raise ValueError(
                'Failed to cleanup description:\n{0}'.format(cleanup_error),
            )


class NewsList(UserList):
    """Project news list."""

    @classmethod
    @validate_call
    def from_url(cls, url: HttpUrl):
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
            with request.urlopen(str(url), timeout=5) as res:  # noqa: S310
                return cls.from_md(res.read().decode('utf-8'))
        except (URLError, ValueError, TimeoutError) as urlopen_error:
            raise ValueError(
                "Failed to load news from '{0}':\n{1}".format(
                    url, urlopen_error,
                ),
            )

    @classmethod
    def from_md(cls, md: AnnotatedStr):
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
            news_list.append(News(match))
        return cls(news_list)
