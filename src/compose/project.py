# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Project utilities."""


import re
from functools import cached_property
from typing import Annotated, List, Optional
from urllib import request
from urllib.error import URLError

from license import License, SpdxLicenseList
from manifest import Manifest
from pydantic import (
    EmailStr,
    Field,
    HttpUrl,
    ValidationError,
    computed_field,
    validate_call,
)
from pydantic_utils import AnnotatedStr, AnnotatedStrList, BaseModelForbidExtra
from repository import Repository


class Contact(BaseModelForbidExtra):
    """Contact configuration schema."""

    name: AnnotatedStr
    email: EmailStr


class Project(BaseModelForbidExtra):
    """Project configuration schema."""

    repository: HttpUrl
    contact: Contact
    featured: Optional[bool] = False
    categories: Optional[AnnotatedStrList] = None

    @computed_field
    @cached_property
    def manifest(self) -> Manifest:
        """
        Get manifest from repository.

        Returns:
            Manifest: project manifest.

        Raises:
            ValueError: If loading the manifest fails.
        """
        try:
            repository = Repository.create(self.repository)
        except (ValidationError, ValueError) as repository_error:
            raise ValueError(
                "Failed to load repository from '{0}':\n{1}".format(
                    self.repository, repository_error,
                ),
            )
        try:
            return Manifest.from_repository(repository)
        except (ValidationError, ValueError) as manifest_error:
            raise ValueError("Failed to load manifest from '{0}':\n{1}".format(
                repository.url, manifest_error,
            ))

    @computed_field
    @cached_property
    def description(self) -> str:
        """
        Get manifest from repository.

        Returns:
            str: description string.

        Raises:
            ValueError: If loading the description fails.
        """
        url = str(self.manifest.description)
        try:
            with request.urlopen(url, timeout=5) as res:  # noqa: S310
                md = res.read().decode('utf-8')
        except (URLError, ValueError, TimeoutError) as urlopen_error:
            raise ValueError(
                "Failed to load description from '{0}':\n{1}".format(
                    url, urlopen_error,
                ),
            )
        try:
            sections = re.split('(^#.*$)', md, flags=re.MULTILINE)
        except (re.error, TypeError) as split_error:
            raise ValueError('Failed to split sections:\n{0}'.format(
                split_error,
            ))
        for section in sections:
            md = re.sub('<!--(.*?)-->', '', section, flags=re.DOTALL).strip()
            if not md.startswith('#') and md:
                return md
        raise ValueError('Failed to parse Markdown description.')

    @computed_field
    @cached_property
    def licenses(self) -> List[License]:
        """
        Get licenses from SPDX license list data.

        Returns:
             List[License]: license list.

        Raises:
            ValueError: If loading the license list fails.
        """
        licenses = []
        try:
            for license_id in self.manifest.licenses:
                licenses.append(SpdxLicenseList.get_license(license_id))
        except (ValidationError, ValueError) as license_error:
            raise ValueError('Failed to load licenses:\n{0}'.format(
                license_error,
            ))
        return licenses

    @validate_call
    def hugo(self) -> str:
        """
        Generate Hugo content.

        Returns:
            str: Hugo content string.
        """
        
        try:
            front_matter = yaml.safe_dump(self.model_dump(
                exclude_none=True, exclude={'md', 'description'},
            ))
        except yaml.YAMLError as yaml_error:
            raise ValueError('Failed to dump YAML front matter:\n{0}'.format(
                yaml_error,
            ))
        return '---\n{0}---\n{1}'.format(front_matter, self.description)
        return '---\ntitle: {0}\n---\n{1}'.format(self.name, self.description)


ProjectList = Annotated[list[Project], Field(min_length=1)]
