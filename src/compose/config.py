# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load configuration."""


from http import HTTPMethod, HTTPStatus
from typing import Annotated, Any, Literal, Optional
from urllib import request
from urllib.error import URLError

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    StringConstraints,
    field_validator,
)

StrWithConstraints = Annotated[str, StringConstraints(
    strip_whitespace=True,
    min_length=1,
)]

ListStrWithConstraintsWithField = Annotated[list[StrWithConstraints], Field(
    min_length=1,
)]


ListHttpUrlWithField = Annotated[list[HttpUrl], Field(min_length=1)]


class LinkConfig(BaseModel, extra='forbid'):
    """Represents a link configuration."""

    name: StrWithConstraints
    url: HttpUrl

    @field_validator('url')
    @classmethod
    def url_must_be_reachable(cls, url: str) -> str:
        """
        Check if URL is reachable.

        Parameters:
            url: URL string.

        Returns:
            URL string.

        Raises:
            ValueError: if the URL is not reachable.
        """
        req = request.Request(url, method=HTTPMethod.HEAD)
        try:
            with request.urlopen(req, timeout=5) as res:  # noqa: S310
                if res.status != HTTPStatus.OK:
                    raise ValueError("Status code: '{0}'.".format(res.status))
        except (URLError, ValueError) as error:
            error_fmt = "Failed to access URL: '{0}'."
            raise ValueError(error_fmt.format(url)) from error
        return url


ListLinkConfigWithField = Annotated[list[LinkConfig], Field(min_length=1)]


class ProjConfig(BaseModel, extra='forbid'):
    """Loads project configuration."""

    version: Literal['1.0.0']
    name: StrWithConstraints
    description: StrWithConstraints
    website: HttpUrl
    licenses: ListStrWithConstraintsWithField
    images: Optional[ListHttpUrlWithField] = None
    documentation: Optional[HttpUrl] = None
    issues: Optional[HttpUrl] = None
    latest_release: Optional[HttpUrl] = None
    forum: Optional[HttpUrl] = None
    newsfeed: Optional[HttpUrl] = None
    links: Optional[ListLinkConfigWithField] = None
    categories: Optional[ListStrWithConstraintsWithField] = None

    @field_validator(
        'website',
        'images',
        'documentation',
        'issues',
        'latest_release',
        'forum',
        'newsfeed',
    )
    @classmethod
    def urls_must_be_reachable(cls, field_value: Any) -> Any:
        """
        Check if URLs are reachable.

        Parameters:
            field_value: URL string or list of URL strings.

        Returns:
            URL string or list of URL strings.
        """
        if isinstance(field_value, list):
            for url in field_value:
                LinkConfig.url_must_be_reachable(url)
        else:
            LinkConfig.url_must_be_reachable(field_value)
        return field_value
