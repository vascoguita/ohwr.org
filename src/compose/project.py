# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Compose project content."""


from typing import Optional

import yaml
from pydantic import NewPath, validate_call
from pydantic_utils import (
    AnnotatedStr,
    AnnotatedStrList,
    BaseModelForbidExtra,
    SerializableUrlList,
)


class Project(BaseModelForbidExtra):
    """Project content."""

    title: AnnotatedStr
    images: Optional[SerializableUrlList] = None
    featured: Optional[bool] = False
    categories: Optional[AnnotatedStrList] = None

    @validate_call
    def dump(self, path: NewPath):
        hugo_content = (
            '---\n' +
            '{0}' +
            '---\n' +
            '{{{{< project >}}}}\n' +
            '{{{{< /project >}}}}\n' +
            '{{{{< latest-news >}}}}'
        ).format(yaml.safe_dump(self.model_dump()))
        with open(path, 'w') as content_file:
            content_file.write(hugo_content)
