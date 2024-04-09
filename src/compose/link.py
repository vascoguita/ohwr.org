# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Link configuration."""


from typing import Annotated

from pydantic import Field
from pydantic_utils import AnnotatedStr, BaseModelForbidExtra, Url


class Link(BaseModelForbidExtra):
    """Represents a link configuration."""

    name: AnnotatedStr
    url: Url


LinkList = Annotated[list[Link], Field(min_length=1)]
