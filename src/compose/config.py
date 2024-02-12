# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load configuration."""


import json
from http import HTTPMethod, HTTPStatus
from typing import Annotated, Any, Literal, Optional
from urllib import request
from urllib.error import URLError

# isort: off

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    StringConstraints,
    field_validator,
)

# isort: on

StrWithConstraints = Annotated[str, StringConstraints(
    strip_whitespace=True,
    min_length=1,
)]

ListStrWithConstraintsWithField = Annotated[list[StrWithConstraints], Field(
    min_length=1,
)]


ListHttpUrlWithField = Annotated[list[HttpUrl], Field(min_length=1)]


class UrlValidator(object):
    """Checks if a URL is reachable."""

    @classmethod
    def url_must_be_reachable(cls, url: str) -> str:
        """
        Check if the URL is reachable.

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


class LinkConfig(BaseModel, extra='forbid'):
    """Represents a link configuration."""

    name: StrWithConstraints
    url: HttpUrl

    @field_validator('url')
    @classmethod
    def validate_url(cls, field_value: Any) -> Any:
        """
        Check if the URL is reachable.

        Parameters:
            field_value: URL string.

        Returns:
            URL string.
        """
        return UrlValidator.url_must_be_reachable(field_value)


ListLinkConfigWithField = Annotated[list[LinkConfig], Field(min_length=1)]


class LicenseValidator(object):
    """Checks if a string is a valid SPDX license identifier."""

    _instance = None
    _spdx_license_list = None

    def __new__(cls):
        """
        Create an instance of LicenseValidator if it doesn't already exist.

        Returns:
            LicenseValidator singleton instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def config(cls, license_list_path: str):
        """
        Configure the SPDX license list from a JSON file.

        Parameters:
            license_list_path: file path to the SPDX JSON license list.
        """
        with open(license_list_path, 'r') as license_list_file:
            cls._spdx_license_list = json.load(license_list_file)

    @classmethod
    def is_valid_spdx_license(cls, license: str) -> str:
        """
        Check if the string is a valid SPDX license identifier.

        Parameters:
            license: license identifier string.

        Returns:
            license identifier string.

        Raises:
            ValueError: if the string is not a valid SPDX license identifier.
        """
        if cls._spdx_license_list:
            for spdx_license in cls._spdx_license_list['licenses']:
                if spdx_license['licenseId'] == license:
                    return license
        error_fmt = "Unknown SPDX license identifier: '{0}'."
        raise ValueError(error_fmt.format(license))


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
    def validate_urls(cls, field_value: Any) -> Any:
        """
        Check if the URLs are reachable.

        Parameters:
            field_value: URL string or list of URL strings.

        Returns:
            URL string or list of URL strings.
        """
        if isinstance(field_value, list):
            for url in field_value:
                UrlValidator.url_must_be_reachable(url)
        else:
            UrlValidator.url_must_be_reachable(field_value)
        return field_value

    @field_validator('licenses')
    @classmethod
    def validate_licenses(cls, field_value: Any) -> Any:
        """
        Check if the licences are valid SPDX license identifiers.

        Parameters:
            field_value: list of license identifiers.

        Returns:
            list of license identifiers.
        """
        for url in field_value:
            LicenseValidator.is_valid_spdx_license(url)
        return field_value
