# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Compose project content."""


from typing import Annotated, Optional

import yaml
from config import Contact
from license import LicenseList
from manifest import LinkList
from pydantic import Field, NewPath, validate_call
from pydantic_utils import (
    AnnotatedStr,
    AnnotatedStrList,
    BaseModelForbidExtra,
    SerializableUrl,
    SerializableUrlList,
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
            path: The file path where the content will be saved.
        """
        hugo_content = (
            '---\n' +
            '{0}' +
            '---\n' +
            '{{{{< project >}}}}\n' +
            '{1}\n' +
            '{{{{< /project >}}}}\n' +
            '{{{{< latest-news >}}}}'
        ).format(
            yaml.safe_dump(
                self.model_dump(exclude_none=True, exclude={'description'}),
            ),
            self.description,
        )
        with open(path, 'w') as content_file:
            content_file.write(hugo_content)
