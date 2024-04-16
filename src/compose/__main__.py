# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Generate content for ohwr.org."""

import argparse
import logging
import sys

from config import Config
from pydantic import ValidationError
from repository import Repository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',  # noqa: WPS323
)

parser = argparse.ArgumentParser()
parser.add_argument('config', type=argparse.FileType('r'))
args = parser.parse_args()

logging.info("Loading configuration from '{0}'...".format(args.config.name))

try:
    config = Config.from_yaml(args.config.read())
except (ValidationError, ValueError) as config_error:
    logging.error(
        'Failed to load configuration:\n{0}'.format(config_error),
    )
    sys.exit(1)

for project in config.projects:
    logging.info(
        "Loading project manifest from '{0}'...".format(project.repository),
    )
    try:
        repository = Repository.create(project.repository)
    except (ValidationError, ValueError) as repository_error:
        logging.error(
            "Failed to parse project repository '{0}':\n{1}".format(
                project.repository, repository_error,
            ),
        )
        continue
    try:
        manifest_yaml = repository.get_file('.ohwr.yaml')
    except (
        ValidationError, ValueError, ConnectionError, RuntimeError,
    ) as manifest_error:
        logging.error(
            "Failed to fetch project manifest from '{0}':\n{1}".format(
                project.repository, manifest_error,
            ),
        )
