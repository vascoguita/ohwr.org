# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load licenses."""


import json

from pydantic import FilePath, ValidationError, validate_call
from pydantic_utils import AnnotatedStr, BaseModelForbidExtra, SerializableUrl


class License(BaseModelForbidExtra):
    """License data."""

    name: AnnotatedStr
    url: SerializableUrl


class SpdxLicenseList:
    """SPDX license list data."""

    _spdx_license_list: dict = {}

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
            cls._spdx_license_list = json.loads(licenses_json)
        except (TypeError, json.JSONDecodeError) as json_error:
            raise ValueError('Failed to load JSON license list:\n{0}'.format(
                json_error,
            ))

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
    def get_license(cls, license_id: AnnotatedStr) -> License:
        """
        Find license data for an SPDX license identifier.

        Parameters:
            license_id: license identifier string.

        Returns:
            License: The License object.

        Raises:
            ValueError: if no data was found for an SPDX license identifier.
        """
        for license in cls._spdx_license_list['licenses']:
            if license['licenseId'] == license_id:
                try:
                    return License(
                        name=license['name'], url=license['reference'],
                    )
                except (ValidationError, KeyError) as license_error:
                    raise ValueError(
                        "Failed to load license '{0}':\n{1}".format(
                            license_id, license_error,
                        ),
                    )
        raise ValueError("Unknown SPDX license identifier '{0}'.".format(
            license_id,
        ))
