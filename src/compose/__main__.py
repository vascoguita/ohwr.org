# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Generate content for ohwr.org."""

import argparse
import logging
import sys

from config import Config
from manifest import Manifest
from pydantic import ValidationError
from spdx import Spdx

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

logging.info("Loading SPDX license list from '{0}'...".format(config.licenses))
try:
    Spdx.from_file(config.licenses)
except (ValidationError, ValueError) as license_error:
    logging.error(
        'Failed to load SPDX license list:\n{0}'.format(license_error),
    )
    sys.exit(1)

for project in config.projects:
    logging.info("Loading manifest from '{0}'...".format(project.repository))
    try:
        manifest = Manifest.from_repository(project.repository)
    except (ValidationError, ValueError) as manifest_error:
        logging.error(
            "Failed to load manifest '{0}':\n{1}".format(
                project.repository, manifest_error,
            ),
        )
