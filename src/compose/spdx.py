# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""SPDX license utilities."""


import json
from typing import Annotated

from pydantic import AfterValidator, Field, FilePath, validate_call
from pydantic_utils import AnnotatedStr


class Spdx:
    """SPDX license list data singleton."""

    _licenses: dict = None

    @classmethod
    @validate_call
    def from_json(cls, licenses_json: AnnotatedStr):
        """
        Load SPDX license list data from JSON.

        Parameters:
            licenses_json: SPDX license list data JSON string.

        Raises:
            ValueError: if JSON is not valid.
        """
        try:
            cls._licenses = json.loads(licenses_json)
        except json.JSONDecodeError as json_error:
            raise ValueError(
                'Failed to load JSON license list:\n{0}'.format(json_error),
            )

    @classmethod
    @validate_call
    def from_file(cls, licenses: FilePath):
        """
        Load SPDX license list data from JSON file.

        Parameters:
            licenses: SPDX license list data JSON file path.

        Raises:
            ValueError: if file is not valid.
        """
        try:
            with open(licenses) as licenses_file:
                cls.from_json(licenses_file.read())
        except (ValueError, FileNotFoundError) as file_error:
            raise ValueError(
                "Failed to load license list file '{0}':\n{1}".format(
                    licenses, file_error,
                ),
            )

    @classmethod
    @validate_call
    def get_license(cls, license_id: AnnotatedStr) -> dict:
        """
        Find license data for an SPDX license identifier.

        Parameters:
            license_id: license identifier string.

        Returns:
            dict: license data.

        Raises:
            ValueError: if no data was found for an SPDX license identifier.
        """
        if cls._licenses:
            for license in cls._licenses['licenses']:
                if license['licenseId'] == license_id:
                    return license
        raise ValueError("No license data found for '{0}'.".format(license_id))


def is_spdx(license_id: AnnotatedStr) -> AnnotatedStr:
    """
    Check if the string is a valid SPDX license identifier.

    Parameters:
        license_id: license identifier string.

    Returns:
        License identifier string.

    Raises:
        ValueError: if the string is not a valid SPDX license identifier.
    """
    try:
        Spdx.get_license(license_id)
    except ValueError as spdx_error:
        raise ValueError(
            "Unknown SPDX license identifier '{0}':\n{1}".format(
                license_id, spdx_error,
            ),
        )
    return license_id


License = Annotated[AnnotatedStr, AfterValidator(is_spdx)]
LicenseList = Annotated[list[License], Field(min_length=1)]
