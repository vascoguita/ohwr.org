# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Custom Pydantic utilities."""


from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


class BaseModelForbidExtra(BaseModel, extra='forbid'):
    """Custom base class for Pydantic models with extra='forbid'."""


AnnotatedStr = Annotated[str, StringConstraints(
    strip_whitespace=True,
    min_length=1,
)]
AnnotatedStrList = Annotated[list[AnnotatedStr], Field(min_length=1)]
