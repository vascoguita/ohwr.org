# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Parse and validate license."""

from link import Link


class LicenseError(Exception):
    """Failed to validate license."""


class License(Link):
    """Parses and validates license."""

    @classmethod
    def from_id(cls, license_id: str, spdx_license_list: dict):
        """
        Construct a License object from an SPDX license identifier.

        Parameters:
            license_id: SPDX license identifier.
            spdx_license_list: SPDX license data list.

        Returns:
            License object.

        Raises:
            LicenseError: if license_id is not a valid SPDX license identifier.
        """
        for license in spdx_license_list['licenses']:
            if license['licenseId'] == license_id:
                return cls(name=license['name'], url=license['reference'])
        msg = 'License ID is not a valid SPDX license ID: {0}'
        raise LicenseError(msg.format(license_id))
