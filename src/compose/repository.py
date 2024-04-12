# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Handle git repositories."""

import os
import subprocess  # noqa: S404
from abc import ABC, abstractmethod
from tempfile import TemporaryDirectory
from urllib import request
from urllib.error import URLError

from pydantic import HttpUrl, ValidationError, validate_call
from pydantic_utils import AnnotatedStr, BaseModelForbidExtra


class Repository(BaseModelForbidExtra, ABC):
    """Abstract base class representing a repository."""

    @abstractmethod
    def get_file(self, filename: str):
        """
        Abstract method to get a file from the repository.

        Args:
            filename: The name of the file to retrieve.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """

    @classmethod
    @validate_call
    def create(cls, url: HttpUrl):
        """
        Create a repository object based on the provided URL.

        Parameters:
            url: Repository URL.

        Returns:
            Union[GitHubRepository, GenericRepository]: Repository object.

        Raises:
            ValueError: If parsing url or creating repository fails.
        """
        if url.host == 'github.com':
            try:
                return GitHubRepository.from_url(url)
            except (ValidationError, ValueError) as github_error:
                raise ValueError(
                    "GitHub repository '{0}' is not valid:\n{1}".format(
                        url, github_error,
                    ),
                )
        else:
            try:
                return GenericRepository(url=url)
            except ValidationError as generic_error:
                raise ValueError(
                    "Generic repository '{0}' is not valid:\n{1}".format(
                        url, generic_error,
                    ),
                )


class GitHubRepository(Repository):
    """Represents a GitHub repository."""

    owner: AnnotatedStr
    repo: AnnotatedStr

    @validate_call
    def get_file(self, filename: AnnotatedStr):
        """
        Get the content of a file from the repository.

        Parameters:
            filename: The name of the file to retrieve.

        Returns:
            Response: The response object containing the content of the file.

        Raises:
            ConnectionError: If requesting the file content fails.
        """
        req = request.Request(
            'https://api.github.com/repos/{0}/{1}/contents/{2}'.format(
                self.owner, self.repo, filename,
            ),
            headers={'Accept': 'application/vnd.github.v3.raw'},
        )
        try:
            with request.urlopen(req, timeout=5) as response:  # noqa: S310
                return response
        except (URLError, ValueError) as url_error:
            raise ConnectionError(
                "Failed to request '{0}':\n{1}".format(
                    req.full_url, url_error,
                ),
            )

    @classmethod
    @validate_call
    def from_url(cls, url: HttpUrl):
        """
        Create a GitHubRepository object from a given URL.

        Args:
            url: The URL of the GitHub repository.

        Returns:
            GitHubRepository: GitHubRepository object.

        Raises:
            ValueError: If parsing the repository URL fails.
        """
        parts = url.path.removeprefix('/').split('/', 1)
        try:
            owner = parts[0]
        except IndexError as owner_error:
            raise ValueError(
                "Failed to parse repository owner from '{0}':\n{1}".format(
                    url, owner_error,
                ),
            )
        try:
            repo = parts[1].removesuffix('.git')
        except IndexError as repo_error:
            raise ValueError(
                "Failed to parse repository name from '{0}':\n{1}".format(
                    url, repo_error,
                ),
            )
        try:
            return cls(owner=owner, repo=repo)
        except ValidationError as github_error:
            raise ValueError(
                "GitHub repository '{0}' is not valid:\n{1}".format(
                    url, github_error,
                ),
            )


class GenericRepository(Repository):
    """Represents a generic repository."""

    url: HttpUrl

    @validate_call
    def get_file(self, filename: AnnotatedStr):
        """
        Get the content of a file from the repository.

        Args:
            filename: The name of the file to retrieve.

        Returns:
            TextIO: The file object containing the content of the file.

        Raises:
            RuntimeError: If cloning the repository fails.
            ValueError: If the specified file is not found in the repository.
        """
        tmpdir = TemporaryDirectory().name
        try:
            subprocess.check_output(
                'git clone --depth 1 {0} {1}'.format(self.url, tmpdir),
                stderr=subprocess.STDOUT,
                shell=True,  # noqa: S602
            )
        except subprocess.CalledProcessError as clone_error:
            raise RuntimeError(
                "Failed to clone '{0}':\n{1}".format(self.url, clone_error),
            )
        try:
            with open(os.path.join(tmpdir, filename)) as repository_file:
                return repository_file
        except FileNotFoundError as file_error:
            raise ValueError(
                "File '{0}' not found in '{1}':\n{2}".format(
                    filename, self.url, file_error,
                ),
            )
