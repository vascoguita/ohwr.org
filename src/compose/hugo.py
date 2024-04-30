# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Compose Hugo content."""


import datetime
from typing import Optional

import yaml
from config import Contact
from license import LicenseList
from manifest import LinkList
from pydantic import NewPath, validate_call
from pydantic_utils import (
    AnnotatedStr,
    AnnotatedStrList,
    BaseModelForbidExtra,
    SerializableUrl,
    SerializableUrlList,
)


class Hugo(BaseModelForbidExtra):
    """Hugo content."""

    front_matter: dict
    markdown: AnnotatedStr

    @validate_call
    def dump(self, path: NewPath):
        """
        Write content to a file.

        Parameters:
            path: The file path where the content will be saved.

        Raises:
            ValueError: If the content cannot be written to a file.
        """
        try:
            front_matter = yaml.safe_dump(self.front_matter)
        except yaml.YAMLError as yaml_error:
            raise ValueError(
                'Failed to dump YAML front matter:\n{0}'.format(yaml_error),
            )
        try:
            with open(path, 'w') as content_file:
                content_file.write(
                    '---\n{0}---\n{1}'.format(front_matter, self.markdown),
                )
        except OSError as open_error:
            raise ValueError(
                "Failed to open file '{0}':\n{1}".format(path, open_error),
            )


class Project(BaseModelForbidExtra):
    """Project content."""

    title: AnnotatedStr
    images: Optional[SerializableUrlList] = None
    categories: Optional[AnnotatedStrList] = None
    featured: Optional[bool] = False
    website: SerializableUrl
    latest_release: Optional[SerializableUrl] = None
    documentation: Optional[SerializableUrl] = None
    repository: Optional[SerializableUrl] = None
    issues: Optional[SerializableUrl] = None
    forum: Optional[SerializableUrl] = None
    links: Optional[LinkList] = None
    contact: Contact
    licenses: LicenseList
    description: AnnotatedStr

    @validate_call
    def dump(self, path: NewPath):
        """
        Write content to a file.

        Parameters:
            path: The file path where the project content will be saved.
        """
        front_matter = self.model_dump(
            exclude_none=True, exclude={'description'},
        )
        markdown = (
            '{{{{< project >}}}}\n{0}\n{{{{< /project >}}}}\n' +
            '{{{{< latest-news >}}}}'
        ).format(self.description)
        Hugo(front_matter=front_matter, markdown=markdown).dump(path)


class News(BaseModelForbidExtra):
    """News content."""

    title: AnnotatedStr
    date: datetime.date
    images: Optional[SerializableUrlList] = None
    topics: AnnotatedStrList
    description: AnnotatedStr

    @validate_call
    def dump(self, path: NewPath):
        """
        Write content to a file.

        Parameters:
            path: The file path where the news content will be saved.
        """
        front_matter = self.model_dump(
            exclude_none=True, exclude={'description'},
        )
        Hugo(front_matter=front_matter, markdown=self.description).dump(path)
