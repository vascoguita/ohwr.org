# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Project category utilities."""


import os
from pathlib import Path
from typing import Annotated

from pydantic import (
    DirectoryPath,
    Field,
    RootModel,
    ValidationError,
    validate_call,
)
from pydantic_utils import AnnotatedStr, BaseModelForbidExtra


class Category(BaseModelForbidExtra):
    """Project category."""

    name: AnnotatedStr
    description: AnnotatedStr

    def hugo(self) -> str:
        """
        Generate Hugo content.

        Returns:
            str: Hugo content string.
        """
        return '---\ntitle: {0}\n---\n{1}'.format(self.name, self.description)

    @validate_call
    def dump(self, path: Path):
        """
        Dump Hugo content.

        Parameters:
            path: Hugo content file path.

        Raises:
            ValueError: if dumping the Hugo content fails.
        """
        dirname = os.path.dirname(path)
        try:
            os.makedirs(dirname)
        except OSError as makedirs_error:
            raise ValueError(
                "Failed to create '{0}' directory:\n{1}".format(
                    dirname, makedirs_error,
                ),
            )
        try:
            with open(path, 'w') as category_file:
                category_file.write(self.hugo())
        except OSError as open_error:
            raise ValueError(
                "Failed to write file '{0}':\n{1}".format(path, open_error),
            )


CategoryList = Annotated[list[Category], Field(min_length=1)]


class CategoryGenerator(RootModel):
    """Project category generator."""

    root: CategoryList

    @validate_call
    def dump(self, sources: DirectoryPath):
        """
        Dump Hugo content.

        Parameters:
            sources: Hugo sources directory.

        Raises:
            ValueError: if dumping the Hugo content fails.
        """
        for category in self.root:
            try:
                path = os.path.join(
                    sources,
                    'content/categories',
                    category.name.lower().replace(' ', '-'),
                    '_index.md',
                )
            except (TypeError, AttributeError, BytesWarning) as join_error:
                raise ValueError(
                    "Failed to define category path for '{0}':\n{1}".format(
                        category.name, join_error,
                    ),
                )
            try:
                category.dump(path)
            except (ValueError, ValidationError) as dump_error:
                raise ValueError(
                    "Failed to dump category '{0}':\n{1}".format(
                        category.name, dump_error,
                    ),
                )
