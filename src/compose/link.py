# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Parse and validate link."""

from pydantic import BaseModel
from url import URL


class Link(BaseModel, extra='forbid'):
    """Parses and validates link."""

    name: str
    url: URL
