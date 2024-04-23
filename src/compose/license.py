# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load licenses."""


import json
from collections import UserDict
from typing import Annotated

from pydantic import Field, FilePath, ValidationError, validate_call
from pydantic_utils import AnnotatedStr, BaseModelForbidExtra, SerializableUrl


class License(BaseModelForbidExtra):
    """License data."""

    name: AnnotatedStr
    url: SerializableUrl


LicenseList = Annotated[list[License], Field(min_length=1)]


class SpdxLicenseList(UserDict):
    """SPDX license list data."""

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
            return cls(json.loads(licenses_json))
        except (TypeError, json.JSONDecodeError) as json_error:
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
                return cls.from_json(licenses_file.read())
        except (ValueError, FileNotFoundError) as file_error:
            raise ValueError(
                "Failed to load license list file '{0}':\n{1}".format(
                    licenses, file_error,
                ),
            )

    @validate_call
    def get_license(self, license_id: AnnotatedStr) -> License:
        """
        Find license data for an SPDX license identifier.

        Parameters:
            license_id: license identifier string.

        Returns:
            License: The License object.

        Raises:
            ValueError: if no data was found for an SPDX license identifier.
        """
        for license in self['licenses']:
            if license['licenseId'] == license_id:
                try:
                    return License(name=license['name'], url=license['reference'])
                except (ValidationError, KeyError) as license_error:
                    raise ValueError(
                        "Failed to load license '{0}':\n{1}".format(
                            license_id, license_error,
                        ),
                    )
        raise ValueError(
            "Unknown SPDX license identifier '{0}'.".format(license_id),
        )
