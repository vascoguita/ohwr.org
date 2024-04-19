# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Compose project content."""


from typing import Optional

from pydantic import HttpUrl, NewPath, validate_call
import yaml
from pydantic_utils import AnnotatedStr, AnnotatedStrList, BaseModelForbidExtra


class Project(BaseModelForbidExtra):
    """Project content."""

    title: AnnotatedStr
    images: Optional[list[HttpUrl]] = None
    featured: Optional[bool] = False
    categories: Optional[AnnotatedStrList] = None

    @validate_call
    def dump(self):
        print(yaml.safe_dump(self.model_dump()))