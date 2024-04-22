# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Compose project content."""


from typing import Optional

import yaml
from pydantic import validate_call
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
    def dump(self):
        fmt = (
            '---\n' +
            '{0}' +
            '---\n' +
            '{{{{< project >}}}}\n' +
            '{{{{< latest-news >}}}}'
        )
        #print(fmt.format(
        #    yaml.safe_dump(self.model_dump())
        #))
