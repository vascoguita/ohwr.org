# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Category configuration and validation utilities."""


from typing import Annotated

from pydantic import AfterValidator, Field
from pydantic_utils import AnnotatedStr, BaseModelForbidExtra


class Category(BaseModelForbidExtra):
    """Represents a category configuration."""

    name: AnnotatedStr
    description: AnnotatedStr


CategoryList = Annotated[list[Category], Field(min_length=1)]


class CategoryValidator:
    """Utility class for category validation."""

    _categories: list[Category] = None

    @classmethod
    def config(cls, categories: list[Category]):
        """
        Configure the category list for validation.

        Parameters:
            categories: categories from the config.yaml file.
        """
        cls._categories = categories

    @classmethod
    def exists(cls, category_name: AnnotatedStr) -> AnnotatedStr:
        """
        Check if the string is an existing category name.

        Parameters:
            category_name: category name.

        Returns:
            Category name.

        Raises:
            ValueError: if the string is not an existing category name.
        """
        if cls._categories:
            for category in cls._categories:
                if category.name == category_name:
                    return category_name
        error_fmt = "Unknown category name: '{0}'."
        raise ValueError(error_fmt.format(category_name))


CategoryName = Annotated[AnnotatedStr, AfterValidator(
    CategoryValidator.exists,
)]
CategoryNameList = Annotated[list[CategoryName], Field(min_length=1)]
