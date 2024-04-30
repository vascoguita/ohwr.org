# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load description."""

import re
from collections import UserString
from urllib import request
from urllib.error import URLError

from pydantic import HttpUrl, ValidationError, validate_call
from pydantic_utils import AnnotatedStr


class Description(UserString):
    """Project description string."""

    @classmethod
    @validate_call
    def from_url(cls, url: HttpUrl):
        """
        Load description from a URL.

        Parameters:
            url: Description URL.

        Returns:
            Description object.

        Raises:
            ValueError: if loading the description fails.
        """
        try:
            with request.urlopen(str(url), timeout=5) as res:  # noqa: S310
                return cls.from_md(res.read().decode('utf-8'))
        except (URLError, ValueError, TimeoutError) as urlopen_error:
            raise ValueError(
                "Failed to load description from '{0}':\n{1}".format(
                    url, urlopen_error,
                ),
            )

    @classmethod
    @validate_call
    def from_md(cls, md: AnnotatedStr):
        """
        Load description from Markdown.

        Parameters:
            md: Markdown description.

        Returns:
            Description object.

        Raises:
            ValueError: if loading the description fails.
        """
        try:
            md = re.sub('<!--(.*?)-->', '', md, flags=re.DOTALL).strip()
        except (re.error, TypeError) as re_error:
            raise ValueError('Failed to process Markdown:\n{0}'.format(
                re_error,
            ))
        while md.startswith('#'):
            try:
                md = md.split('\n', 1)[1].strip()
            except IndexError as split_error:
                raise ValueError(
                    'Failed to fetch Markdown after headings:\n{0}'.format(
                        split_error,
                    ),
                )
        try:
            return cls(md.split('\n#')[0].strip())
        except ValidationError as validation_error:
            raise ValueError('Description is not valid:\n{0}'.format(
                validation_error,
            ))
