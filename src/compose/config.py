# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load configuration."""


from typing import Annotated, Optional

import yaml
from pydantic import (
    DirectoryPath,
    EmailStr,
    Field,
    FilePath,
    ValidationError,
    model_validator,
    validate_call,
)
from pydantic_utils import AnnotatedStr, AnnotatedStrList, BaseModelForbidExtra
from repository import AnnotatedRepository


class Contact(BaseModelForbidExtra):
    """Contact configuration schema."""

    name: AnnotatedStr
    email: EmailStr


class Category(BaseModelForbidExtra):
    """Category configuration schema."""

    name: AnnotatedStr
    description: AnnotatedStr


CategoryList = Annotated[list[Category], Field(min_length=1)]


class Project(BaseModelForbidExtra):
    """Project configuration schema."""

    repository: AnnotatedRepository
    contact: Contact
    featured: Optional[bool] = False
    categories: Optional[AnnotatedStrList] = None


ProjectList = Annotated[list[Project], Field(min_length=1)]


class Config(BaseModelForbidExtra):
    """Main configuration schema."""

    sources: DirectoryPath
    licenses: FilePath
    categories: Optional[CategoryList] = None
    projects: ProjectList

    @model_validator(mode='after')
    def check_categories_match(self) -> 'Config':
        """
        Check if categories in projects match the available categories.

        Returns:
            Config: The configuration object with validated category names.

        Raises:
            ValueError: If an unknown category is found in a project.
        """
        categories = []
        if self.categories:
            for category in self.categories:
                categories.append(category.name)

        for project in self.projects:
            if project.categories:
                unknown = set(project.categories) - set(categories)
                if unknown:
                    raise ValueError(
                        "Project '{0}' with unknown categories: '{1}'.".format(
                            project.repository.url, unknown,
                        ),
                    )
        return self

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
