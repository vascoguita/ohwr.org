# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load manifest."""


import logging
from http import HTTPMethod, HTTPStatus
from typing import Annotated, Literal, Optional
from urllib import request
from urllib.error import URLError

from pydantic import (
    AfterValidator,
    Field,
    HttpUrl,
    ValidationError,
    validate_call,
)
from pydantic_utils import AnnotatedStr, AnnotatedStrList, BaseModelForbidExtra, SerializableUrl, YamlSchema
from repository import Repository


def is_reachable(url: HttpUrl) -> HttpUrl:
    """
    Check if the URL is reachable.

    Parameters:
        url: HTTP URL.

    Returns:
        HTTP URL.

    Raises:
        ValueError: if the URL is not reachable.
    """
    logging.debug("Checking if '{0}' is reachable...".format(url))
    req = request.Request(url, method=HTTPMethod.HEAD)
    try:
        with request.urlopen(req, timeout=5) as res:  # noqa: S310
            if res.status != HTTPStatus.OK:
                raise ValueError("Status code: '{0}'.".format(res.status))
    except (URLError, ValueError, TimeoutError) as urlopen_error:
        raise ValueError(
            "Failed to access URL '{0}':\n{1}".format(url, urlopen_error),
        )
    return url


ReachableUrl = Annotated[SerializableUrl, AfterValidator(is_reachable)]
ReachableUrlList = Annotated[list[ReachableUrl], Field(min_length=1)]


class Link(BaseModelForbidExtra):
    """Link schema."""

    name: AnnotatedStr
    url: ReachableUrl


LinkList = Annotated[list[Link], Field(min_length=1)]


class Manifest(YamlSchema):
    """Manifest schema."""

    version: Literal['1.0.0']
    name: AnnotatedStr
    description: ReachableUrl
    website: ReachableUrl
    licenses: AnnotatedStrList
    images: Optional[ReachableUrlList] = None
    documentation: Optional[ReachableUrl] = None
    issues: Optional[ReachableUrl] = None
    latest_release: Optional[ReachableUrl] = None
    forum: Optional[ReachableUrl] = None
    newsfeed: Optional[ReachableUrl] = None
    links: Optional[LinkList] = None

    @classmethod
    @validate_call
    def from_repository(cls, repository: Repository):
        """
        Load the manifest from Git repository.

        Parameters:
            repository: Git repository.

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
