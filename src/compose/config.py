# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load configuration."""


import json
from typing import Annotated, Any, Literal, Optional

from custom_types import AnnotatedStr, ListAnnotatedStr, ListUrl, Url
from pydantic import BaseModel, Field, field_validator


class LinkConfig(BaseModel, extra='forbid'):
    """Represents a link configuration."""

    name: AnnotatedStr
    url: Url


ListLinkConfigWithField = Annotated[list[LinkConfig], Field(min_length=1)]


class LicenseValidator(object):
    """Checks if a string is a valid SPDX license identifier."""

    _spdx_license_list = None

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


class ExtProjConfig(BaseModel, extra='forbid'):
    """Represents the external configuration for a project."""

    version: Literal['1.0.0']
    name: AnnotatedStr
    description: AnnotatedStr
    website: Url
    licenses: ListAnnotatedStr
    images: Optional[ListUrl] = None
    documentation: Optional[Url] = None
    issues: Optional[Url] = None
    latest_release: Optional[Url] = None
    forum: Optional[Url] = None
    newsfeed: Optional[Url] = None
    links: Optional[ListLinkConfigWithField] = None
    categories: Optional[ListAnnotatedStr] = None

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
        for license in field_value:
            LicenseValidator.is_valid_spdx_license(license)
        return field_value


class IntProjConfig(BaseModel, extra='forbid'):
    """Represents the internal configuration for a project."""

    id: AnnotatedStr
    url: Url
    featured: Optional[bool] = False


ListIntProjConfig = Annotated[list[IntProjConfig], Field(min_length=1)]


class ComposeConfig(BaseModel, extra='forbid'):
    """Loads compose configuration."""

    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    spdx_license_list: AnnotatedStr
    source: AnnotatedStr
    projects: ListIntProjConfig
