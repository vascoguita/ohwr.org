# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load manifest."""


from typing import Annotated, Literal, Optional

import yaml
from pydantic import Field, ValidationError, validate_call
from pydantic_utils import (
    AnnotatedStr,
    BaseModelForbidExtra,
    ReachableUrl,
    ReachableUrlList,
)
from repository import Repository
from spdx import LicenseList


class Link(BaseModelForbidExtra):
    """Link schema."""

    name: AnnotatedStr
    url: ReachableUrl


LinkList = Annotated[list[Link], Field(min_length=1)]


class Manifest(BaseModelForbidExtra):
    """Manifest schema."""

    version: Literal['1.0.0']
    name: AnnotatedStr
    description: ReachableUrl
    website: ReachableUrl
    licenses: LicenseList
    images: Optional[ReachableUrlList] = None
    documentation: Optional[ReachableUrl] = None
    issues: Optional[ReachableUrl] = None
    latest_release: Optional[ReachableUrl] = None
    forum: Optional[ReachableUrl] = None
    newsfeed: Optional[ReachableUrl] = None
    links: Optional[LinkList] = None

    @classmethod
    @validate_call
    def from_yaml(cls, manifest_yaml: AnnotatedStr):
        """
        Load the manifest from YAML.

        Parameters:
            manifest_yaml: manifest YAML string.

        Returns:
            Manifest: The manifest object.

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

    @classmethod
    @validate_call
    def from_repository(cls, repository: Repository):
        """
        Load the manifest from Git repository.

        Parameters:
            repository: Repository child object.

        Returns:
            Manifest: The manifest object.

        Raises:
            ValueError: If loading the manifest fails.
        """
        try:
            manifest_yaml = repository.read('.ohwr.yaml')
        except (
            ValidationError, ValueError, ConnectionError, RuntimeError,
        ) as manifest_error:
            raise ValueError(
                "Failed to fetch '.ohwr.yaml' from '{0}':\n{1}".format(
                    repository.url, manifest_error,
                ),
            )
        try:
            return cls.from_yaml(manifest_yaml)
        except (ValidationError, ValueError) as yaml_error:
            raise ValueError(
                "Failed to parse '.ohwr.yaml' from '{0}':\n{1}".format(
                    repository.url, yaml_error,
                ),
            )
