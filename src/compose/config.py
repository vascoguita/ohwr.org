# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load configuration."""


from typing import Annotated, Literal, Optional

from custom_types import (
    AnnotatedStr,
    ListAnnotatedStr,
    ListUrl,
    SpdxLicense,
    Url,
)
from pydantic import BaseModel, Field


class BaseModelForbidExtra(BaseModel, extra='forbid'):
    """Custom base class for Pydantic models with extra='forbid'."""


class LinkConfig(BaseModelForbidExtra):
    """Represents a link configuration."""

    name: AnnotatedStr
    url: Url


ListLinkConfig = Annotated[list[LinkConfig], Field(min_length=1)]


class ExtProjConfig(BaseModelForbidExtra):
    """Represents the external configuration for a project."""

    version: Literal['1.0.0']
    name: AnnotatedStr
    description: AnnotatedStr
    website: Url
    licenses: Annotated[list[SpdxLicense], Field(min_length=1)]
    images: Optional[ListUrl] = None
    documentation: Optional[Url] = None
    issues: Optional[Url] = None
    latest_release: Optional[Url] = None
    forum: Optional[Url] = None
    newsfeed: Optional[Url] = None
    links: Optional[ListLinkConfig] = None
    categories: Optional[ListAnnotatedStr] = None


class IntProjConfig(BaseModelForbidExtra):
    """Represents the internal configuration for a project."""

    id: AnnotatedStr
    url: Url
    featured: Optional[bool] = False


class CliConfig(BaseModelForbidExtra):
    """Loads CLI configuration."""

    log_level: Optional[
        Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    ] = 'INFO'
    spdx_license_list: Url
    source: AnnotatedStr
    projects: Annotated[list[IntProjConfig], Field(min_length=1)]
