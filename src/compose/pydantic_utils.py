# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Custom Pydantic utilities."""

from typing import Annotated

import yaml
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    PlainSerializer,
    StringConstraints,
    ValidationError,
    validate_call,
)


class BaseModelForbidExtra(BaseModel, extra='forbid'):
    """Custom base class for Pydantic models with extra='forbid'."""


AnnotatedStr = Annotated[str, StringConstraints(
    strip_whitespace=True,
    min_length=1,
)]
AnnotatedStrList = Annotated[list[AnnotatedStr], Field(min_length=1)]


class YamlSchema(BaseModelForbidExtra):
    """Base class for loading Pydantic models from YAML."""

    @classmethod
    @validate_call
    def from_yaml(cls, yaml_str: AnnotatedStr):
        """
        Load model from YAML.

        Parameters:
            yaml_str: YAML string.

        Returns:
            YamlSchema: The YamlSchema object.

        Raises:
            ValueError: If loading the YAML fails.
        """
        try:
            yaml_dict = yaml.safe_load(yaml_str)
        except yaml.YAMLError as yaml_error:
            raise ValueError(
                'Failed to load YAML:\n{0}'.format(yaml_error),
            )
        try:
            return cls(**yaml_dict)
        except (ValidationError, TypeError) as construct_error:
            raise ValueError(
                'Failed to initialize YamlSchema:\n{0}'.format(
                    construct_error,
                ),
            )


def serialize(url: HttpUrl) -> str:
    """
    Serialize an HttpUrl into a string.

    Parameters:
        url: HTTP URL.

    Returns:
        URL string.
    """
    return str(url)


SerializableUrl = Annotated[HttpUrl, PlainSerializer(serialize)]
SerializableUrlList = Annotated[list[SerializableUrl], Field(min_length=1)]
