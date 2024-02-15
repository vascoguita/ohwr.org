# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load configuration."""


from typing import Annotated, Literal, Optional

from custom_types import AnnotatedStr, License, ListAnnotatedStr, ListUrl, Url
from pydantic import BaseModel, Field


class BaseModelForbidExtra(BaseModel, extra='forbid'):
    """Custom base class for Pydantic models with extra='forbid'."""


class LinkConfig(BaseModelForbidExtra):
    """Represents a link configuration."""

    name: AnnotatedStr
    url: Url.get_type()


ListLinkConfig = Annotated[list[LinkConfig], Field(min_length=1)]


class ExtProjConfig(BaseModelForbidExtra):
    """Represents the external configuration for a project."""

    version: Literal['1.0.0']
    name: AnnotatedStr
    description: AnnotatedStr
    website: Url.get_type()
    licenses: Annotated[list[License.get_type()], Field(min_length=1)]
    images: Optional[ListUrl] = None
    documentation: Optional[Url.get_type()] = None
    issues: Optional[Url.get_type()] = None
    latest_release: Optional[Url.get_type()] = None
    forum: Optional[Url.get_type()] = None
    newsfeed: Optional[Url.get_type()] = None
    links: Optional[ListLinkConfig] = None
    categories: Optional[ListAnnotatedStr] = None


class IntProjConfig(BaseModelForbidExtra):
    """Represents the internal configuration for a project."""

    id: AnnotatedStr
    url: Url.get_type()
    featured: Optional[bool] = False


class CliConfig(BaseModelForbidExtra):
    """Loads CLI configuration."""

    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    spdx_license_list: AnnotatedStr
    source: AnnotatedStr
    projects: Annotated[list[IntProjConfig], Field(min_length=1)]
