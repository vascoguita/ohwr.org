# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Fetch files from a repository."""

from dataclasses import dataclass
import os
import subprocess
from tempfile import TemporaryDirectory
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class RepositoryError(Exception):
    """Failed to fetch files from a repository."""


def read(url: str, path: str) -> str:
    if urlparse(url).hostname == 'github.com':
        repo = GitHubRepository
    else:
        repo = GenericRepository
    return repo(url).read(path)


class GenericRepository(object):
    tmpdir: str

    def __init__(self, url: str):
        self.tmpdir = TemporaryDirectory().name
        try:
            subprocess.check_output(
                'git clone --depth 1 {0} {1}'.format(url, self.tmpdir),
                stderr=subprocess.STDOUT,
                shell=True,  # noqa: S602
            )
        except subprocess.CalledProcessError as clone_error:
            msg = 'Failed to clone {0}:\n↳ {1}'
            raise RepositoryError(msg.format(url, clone_error))
    
    def read(self, path: str):
        try:
            with open(os.path.join(self.tmpdir, path)) as file:
                return file.read()
        except FileNotFoundError:
            msg = 'No .ohwr.yaml file found in {0}.'
            raise ConfigError(msg.format(repo))


class GitHubRepository(object):
    owner = segments[-2]
    repo = segments[-1].removesuffix('.git')

    def read(self, path: str) -> str:
        segments = self.split('/')
        self.owner = segments[-2]
        self.repo = segments[-1].removesuffix('.git')
    owner: str
    repo: str
        req = Request(
            'https://api.github.com/repos/{0}/{1}/contents/{2}'.format(
                self.owner,
                self.repo,
                path,
            ),
            headers={'Accept': 'application/vnd.github.v3.raw'},
        )

        try:
            with urlopen(req) as response:
                return response.read().decode()
        except URLError as error:
            msg = 'Failed to request {0}:\n↳ {1}'
            raise GitHubError(msg.format(req.full_url, error))