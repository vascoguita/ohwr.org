# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load configuration."""


from typing import Annotated, Literal, Optional

from pydantic import EmailStr, Field, model_validator
from pydantic_utils import AnnotatedStr, BaseModelForbidExtra, Url


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

    repository: Url
    contact: Contact
    featured: Optional[bool] = False
    categories: Optional[AnnotatedStr] = None


ProjectList = Annotated[list[Project], Field(min_length=1)]


class Config(BaseModelForbidExtra):
    """Main configuration schema."""

    sources: AnnotatedStr
    licenses: AnnotatedStr
    log_level: Optional[
        Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    ] = 'INFO'
    categories: Optional[CategoryList] = None
    projects: ProjectList

    @model_validator(mode='after')
    def check_categories_match(self) -> 'Config':
        """
        Check if categories in projects match the available categories.

        Raises:
            ValueError: If an unknown category is found in a project.

        Returns:
            Config: The configuration object with validated category names.
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
                            project.repository, unknown,
                        ))
        return self
