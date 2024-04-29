# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load configuration."""


from typing import Annotated, Optional

from category import CategoryList
from pydantic import (
    DirectoryPath,
    EmailStr,
    Field,
    FilePath,
    HttpUrl,
    model_validator,
)
from pydantic_utils import (
    AnnotatedStr,
    AnnotatedStrList,
    BaseModelForbidExtra,
    YamlSchema,
)


class Contact(BaseModelForbidExtra):
    """Contact configuration schema."""

    name: AnnotatedStr
    email: EmailStr


class Project(BaseModelForbidExtra):
    """Project configuration schema."""

    repository: HttpUrl
    contact: Contact
    featured: Optional[bool] = False
    categories: Optional[AnnotatedStrList] = None


ProjectList = Annotated[list[Project], Field(min_length=1)]


class Config(YamlSchema):
    """Main configuration schema."""

    sources: DirectoryPath
    licenses: FilePath
    categories: CategoryList
    projects: ProjectList

    @model_validator(mode='after')
    def check_categories_match(self):
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
                            project.repository, unknown,
                        ),
                    )
        return self
