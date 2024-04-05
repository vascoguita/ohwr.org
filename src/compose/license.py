# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""SPDX license validation utilities."""


from typing import Annotated

from link import Link
from pydantic import AfterValidator, Field
from pydantic_utils import AnnotatedStr


class LicenseValidator:
    """Utility class for SPDX license validation."""

    _spdx_license_list: dict = None

    @classmethod
    def config(cls, spdx_license_list: dict):
        """
        Configure the SPDX license list for validation.

        Parameters:
            spdx_license_list: licenses from the SPDX licenses.json file.
        """
        cls._spdx_license_list = spdx_license_list

    @classmethod
    def is_spdx(cls, license_id: AnnotatedStr) -> Link:
        """
        Check if the string is a valid SPDX license identifier.

        Parameters:
            license_id: license identifier string.

        Returns:
            Link object.

        Raises:
            ValueError: if the string is not a valid SPDX license identifier.
        """
        if cls._spdx_license_list:
            for license in cls._spdx_license_list['licenses']:
                if license['licenseId'] == license_id:
                    return Link(name=license['name'], url=license['reference'])
        error_fmt = "Unknown SPDX license identifier: '{0}'."
        raise ValueError(error_fmt.format(license_id))


License = Annotated[AnnotatedStr, AfterValidator(LicenseValidator.is_spdx)]
LicenseList = Annotated[list[License], Field(min_length=1)]
