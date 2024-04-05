# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load configuration."""


from typing import Annotated, Literal, Optional

from category import CategoryList, CategoryNameList
from contact import Contact
from license import LicenseList
from link import LinkList
from pydantic import Field
from pydantic_utils import AnnotatedStr, BaseModelForbidExtra
from url import Url, UrlList


class ExternalProjectConfig(BaseModelForbidExtra):
    """Represents the external configuration for a project."""

    version: Literal['1.0.0']
    name: AnnotatedStr
    description: Url
    website: Url
    licenses: LicenseList
    images: Optional[UrlList] = None
    documentation: Optional[Url] = None
    issues: Optional[Url] = None
    latest_release: Optional[Url] = None
    forum: Optional[Url] = None
    newsfeed: Optional[Url] = None
    links: Optional[LinkList] = None


ExternalProjectConfigList = Annotated[list[ExternalProjectConfig], Field(
    min_length=1,
)]


class InternalProjectConfig(BaseModelForbidExtra):
    """Represents the internal configuration for a project."""

    url: Url
    contact: Contact


class CliConfig(BaseModelForbidExtra):
    """Loads CLI configuration."""

    log_level: Optional[
        Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    ] = 'INFO'
    spdx_license_list: Url
    source: AnnotatedStr
    projects: Optional[UrlList] = None
    categories: Optional[CategoryList] = None
