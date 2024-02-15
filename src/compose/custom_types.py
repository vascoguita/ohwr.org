# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Define custom data types."""

from http import HTTPMethod, HTTPStatus
from typing import Annotated
from urllib import request
from urllib.error import URLError

from pydantic import AfterValidator, Field, HttpUrl, StringConstraints

AnnotatedStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]

ListAnnotatedStr = Annotated[list[AnnotatedStr], Field(min_length=1)]


class Url(object):
    """Utility class for validating reachable HTTP URLs."""

    @classmethod
    def validate(cls, url: HttpUrl) -> HttpUrl:
        """
        Check if the URL is reachable.

        Parameters:
            url: HTTP URL.

        Returns:
            HTTP URL.

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

    @classmethod
    def get_type(cls) -> type[Annotated]:
        """
        Get the Annotated type with HTTP URL validation.

        Returns:
            Annotated type with URL validation.
        """
        return Annotated[HttpUrl, AfterValidator(cls.validate)]


ListUrl = Annotated[list[Url.get_type()], Field(min_length=1)]


class License(object):
    """Utility class for SPDX license validation."""

    _spdx_license_list: dict = None

    @classmethod
    def config(cls, spdx_license_list: dict):
        """
        Configure the SPDX license list for validation.

        Parameters:
            spdx_license_list: licenses from the SPDX licenses.json file.
        """
        cls._spdx_license_list = spdx_license_list

    @classmethod
    def validate(cls, license_id: AnnotatedStr) -> AnnotatedStr:
        """
        Check if the string is a valid SPDX license identifier.

        Parameters:
            license_id: license identifier string.

        Returns:
            License identifier string.

        Raises:
            ValueError: if the string is not a valid SPDX license identifier.
        """
        if cls._spdx_license_list:
            for spdx_license in cls._spdx_license_list['licenses']:
                if spdx_license['licenseId'] == license_id:
                    return license_id
        error_fmt = "Unknown SPDX license identifier: '{0}'."
        raise ValueError(error_fmt.format(license_id))

    @classmethod
    def get_type(cls) -> type[Annotated]:
        """
        Get the Annotated type with SPDX license validation.

        Returns:
            License identifier annotated type.
        """
        return Annotated[AnnotatedStr, AfterValidator(cls.validate)]
