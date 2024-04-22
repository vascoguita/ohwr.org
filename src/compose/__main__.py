# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Generate content for ohwr.org."""

import argparse
import logging
import os
import sys

from config import Config
from manifest import Manifest
from project import Project
from pydantic import ValidationError
from spdx import Spdx

logging.basicConfig(
    level=logging.DEBUG,
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

logging.debug('Defining content directory for projects...')
try:
    projects_dir = os.path.join(config.sources, 'content/projects')
except (TypeError, AttributeError, BytesWarning) as projects_path_error:
    logging.error(
        'Failed to define content directory for projects:\n{0}'.format(
            projects_path_error,
        ),
    )
    sys.exit(1)

logging.debug("Creating '{0}' directory...".format(projects_dir))
try:
    os.makedirs(projects_dir)
except OSError as projects_dir_error:
    logging.error(
        "Failed to create '{0}' directory:\n{1}".format(
            projects_dir, projects_dir_error,
        ),
    )
    sys.exit(1)

for project_config in config.projects:
    logging.info(
        "Loading manifest from '{0}'...".format(
            project_config.repository.url,
        ),
    )
    try:
        manifest = Manifest.from_repository(project_config.repository)
    except (ValidationError, ValueError) as manifest_error:
        logging.error(
            "Failed to load manifest from '{0}':\n{1}".format(
                project_config.repository.url, manifest_error,
            ),
        )
        continue

    logging.info("Generating content for '{0}'...".format(manifest.name))
    try:
        project = Project(
            title=manifest.name,
            images=manifest.images,
            featured=project_config.featured,
            categories=project_config.categories,
        )
    except ValidationError as project_error:
        logging.error(
            "Failed to generate content for '{0}':\n{1}".format(
                manifest.name, project_error,
            ),
        )
        continue

    logging.debug("Defining content path for '{0}'...".format(manifest.name))
    try:
        project_path = os.path.join(
            projects_dir, project_config.repository.project,
        )
    except (TypeError, AttributeError, BytesWarning) as project_path_error:
        logging.error(
            "Failed to define content path for '{0}':\n{1}".format(
                manifest.name, project_path_error,
            ),
        )
        continue

    logging.info(
        "Writing content for '{0}' to '{1}'...".format(
            manifest.name, project_path,
        ),
    )
