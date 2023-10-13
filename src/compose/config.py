# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Fetch, parse and validate configuration."""

import os
import subprocess  # noqa: S404
from datetime import date
from logging import debug, info
from tempfile import TemporaryDirectory
from typing import Literal, Optional, TextIO, Union
from urllib.parse import urlparse

import yaml
from compose.repository import GitHubError, Repo
from pydantic import BaseModel, HttpUrl, ValidationError


class ConfigError(Exception):
    """Failed to fetch, parse or validate configuration."""


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
    """Fetches, parses and validates configuration."""

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
        Fetch configuration from a git repository.

        Parameters:
            repo: git repository URL.

        Returns:
            Config object.

        Raises:
            ConfigError: if fetching the configuration fails.
        """
        info('Fetching .ohwr.yaml from {0}...'.format(repo))
        if urlparse(repo).hostname == 'github.com':
            try:
                return cls.from_yaml(Repo(repo).read('.ohwr.yaml'))
            except GitHubError as github_error:
                msg = 'Failed to fetch .ohwr.yaml from {0}:\n↳ {1}'
                raise ConfigError(msg.format(repo, github_error))
        tmpdir = TemporaryDirectory().name
        try:
            subprocess.check_output(
                'git clone --depth 1 {0} {1}'.format(repo, tmpdir),
                stderr=subprocess.STDOUT,
                shell=True,  # noqa: S602
            )
        except subprocess.CalledProcessError as clone_error:
            msg = 'Failed to clone {0}:\n↳ {1}'
            raise ConfigError(msg.format(repo, clone_error))
        try:
            with open(os.path.join(tmpdir, '.ohwr.yaml')) as yaml_config:
                return cls.from_yaml(yaml_config)
        except FileNotFoundError:
            msg = 'No .ohwr.yaml file found in {0}.'
            raise ConfigError(msg.format(repo))

    @classmethod
    def from_yaml(cls, yaml_config: Union[str, TextIO]):
        """
        Parse and validate YAML configuration.

        Parameters:
            yaml_config: YAML file or string.

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
