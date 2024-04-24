# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Compose category content."""

import yaml
from pydantic import NewPath, validate_call
from pydantic_utils import AnnotatedStr, BaseModelForbidExtra


class Category(BaseModelForbidExtra):
    """Category content."""

    title: AnnotatedStr
    description: AnnotatedStr

    @validate_call
    def dump(self, path: NewPath):
        """
        Write content to a file.

        Parameters:
            path: The file path where the content will be saved.
        """
        hugo_content = '---\n{0}---\n{1}'.format(
            yaml.safe_dump(self.model_dump(include={'title'})),
            self.description,
        )
        with open(path, 'w') as content_file:
            content_file.write(hugo_content)
