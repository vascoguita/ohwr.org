# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load, parse and validate configuration."""

import os
import subprocess  # noqa: S404
from datetime import date
from logging import debug, info
from tempfile import TemporaryDirectory
from typing import Literal, Optional, TextIO, Union
from urllib import request
from urllib.error import URLError
from urllib.parse import urlparse

import yaml
from pydantic import BaseModel, HttpUrl, ValidationError


class ConfigError(Exception):
    """Failed to load, parse or validate configuration."""


class Link(BaseModel, extra='forbid'):
    """Parses and validates link configuration."""

    name: str
    url: HttpUrl


class News(BaseModel, extra='forbid'):
    """Parses and validates news configuration."""

    title: str
    date: date
    image: Optional[HttpUrl] = None
    content: Optional[str] = None  # noqa: WPS110


class Config(BaseModel, extra='forbid'):
    """Loads, parses and validates configuration."""

    version: Literal['1.0.0']
    name: str
    description: str
    website: HttpUrl
    licenses: list[str]
    images: Optional[list[HttpUrl]] = None
    documentation: Optional[HttpUrl] = None
    issues: Optional[HttpUrl] = None
    latest_release: Optional[HttpUrl] = None
    forum: Optional[HttpUrl] = None
    links: Optional[list[Link]] = None
    categories: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    news: Optional[list[News]] = None

    @classmethod
    def from_repo(cls, repo: str):
        """
        Load configuration from a git repository.

        Parameters:
            repo: git repository URL.

        Returns:
            Config object.

        Raises:
            ConfigError: if loading the configuration fails.
        """
        if urlparse(repo).hostname == 'github.com':
            return cls.from_github(repo)
        info('Loading .ohwr.yaml from {0} with git clone...'.format(repo))
        tmpdir = TemporaryDirectory().name
        try:
            subprocess.check_output(
                'git clone --depth 1 {0} {1}'.format(repo, tmpdir),
                stderr=subprocess.STDOUT,
                shell=True,  # noqa: S602
            )
        except subprocess.CalledProcessError as error:
            msg = 'Failed to clone {0}:\n↳ {1}'
            raise ConfigError(msg.format(repo, error))
        try:
            with open(os.path.join(tmpdir, '.ohwr.yaml')) as config_file:
                return cls.from_yaml(config_file)
        except FileNotFoundError:
            msg = 'No .ohwr.yaml file found in {0}.'
            raise ConfigError(msg.format(repo))

    @classmethod
    def from_github(cls, repo: str):
        """
        Load configuration from a GitHub repository.

        Parameters:
            repo: git repository URL.

        Returns:
            Config object.

        Raises:
            ConfigError: if loading the configuration fails.
        """
        info('Loading .ohwr.yaml from {0} with GitHub API...'.format(repo))
        fmt = 'https://api.github.com/repos/{0}/contents/.ohwr.yaml'
        req = request.Request(
            fmt.format(
                urlparse(repo).path.removeprefix('/').removesuffix('.git')
            ),
            headers={'Accept': 'application/vnd.github.v3.raw'},
        )
        try:
            with request.urlopen(req) as response:  # noqa: S310
                return cls.from_yaml(response)
        except URLError as error:
            msg = 'Failed to request {0}:\n↳ {1}'
            raise ConfigError(msg.format(req.full_url, error))

    @classmethod
    def from_yaml(cls, yaml_config: Union[str, TextIO]):
        """
        Parse and validate YAML configuration.

        Parameters:
            config_yaml: YAML file or string.

        Returns:
            Config object.

        Raises:
            ConfigError: if loading or validating the configuration fails.
        """
        debug('Parsing YAML configuration...')
        try:
            config = yaml.safe_load(yaml_config)
        except yaml.YAMLError as yaml_error:
            msg = 'Failed to parse YAML configuration:\n↳ {0}'
            raise ConfigError(msg.format(yaml_error))
        info('Validating YAML configuration...')
        try:
            return cls(**config)
        except (ValidationError, KeyError) as validation_error:
            msg = 'YAML configuration is not valid:\n↳ {0}'
            raise ConfigError(msg.format(validation_error))
