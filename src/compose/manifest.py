# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load manifest."""


from typing import Annotated, Literal, Optional

import yaml
from pydantic import Field, ValidationError, validate_call
from pydantic_utils import AnnotatedStr, BaseModelForbidExtra, Url
from spdx import LicenseList


class Link(BaseModelForbidExtra):
    """Link schema."""

    name: AnnotatedStr
    url: Url


LinkList = Annotated[list[Link], Field(min_length=1)]


class Manifest(BaseModelForbidExtra):
    """Manifest schema."""

    version: Literal['1.0.0']
    name: AnnotatedStr
    description: Url
    website: Url
    licenses: LicenseList
    images: Optional[list[Url]] = None
    documentation: Optional[Url] = None
    issues: Optional[Url] = None
    latest_release: Optional[Url] = None
    forum: Optional[Url] = None
    newsfeed: Optional[Url] = None
    links: Optional[LinkList] = None

    @classmethod
    @validate_call
    def from_yaml(cls, config_yaml: AnnotatedStr):
        """
        Load the configuration from YAML.

        Parameters:
            config_yaml: configuration YAML string.

        Returns:
            Config: The configuration object with validated category names.

        Raises:
            ValueError: If loading the configuration fails.
        """
        try:
            config = yaml.safe_load(config_yaml)
        except yaml.YAMLError as yaml_error:
            raise ValueError(
                'Failed to load YAML configuration:\n{0}'.format(yaml_error),
            )
        try:
            return cls(**config)
        except (ValidationError, TypeError) as config_error:
            raise ValueError(
                'YAML configuration is not valid:\n{0}'.format(config_error),
            )
