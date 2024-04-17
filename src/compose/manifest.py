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
    def from_yaml(cls, manifest_yaml: AnnotatedStr):
        """
        Load the manifest from YAML.

        Parameters:
            manifest_yaml: manifest YAML string.

        Returns:
            Manifest: The manifest object with validated category names.

        Raises:
            ValueError: If loading the manifest fails.
        """
        try:
            manifest = yaml.safe_load(manifest_yaml)
        except yaml.YAMLError as yaml_error:
            raise ValueError(
                'Failed to load YAML manifest:\n{0}'.format(yaml_error),
            )
        try:
            return cls(**manifest)
        except (ValidationError, TypeError) as manifest_error:
            raise ValueError(
                'YAML manifest is not valid:\n{0}'.format(manifest_error),
            )
