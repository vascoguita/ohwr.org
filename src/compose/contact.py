# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Contact configuration."""


from pydantic import EmailStr
from pydantic_utils import AnnotatedStr, BaseModelForbidExtra


class Contact(BaseModelForbidExtra):
    """Represents a contact configuration."""

    name: AnnotatedStr
    email: EmailStr
