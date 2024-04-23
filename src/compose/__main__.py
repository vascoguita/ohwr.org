# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Generate content for ohwr.org."""

import argparse
import logging
import os
import sys

from config import Config
from description import Description
from license import SpdxLicenseList
from manifest import Manifest
from project import Project
from pydantic import ValidationError
from repository import Repository

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
    spdx_licenses = SpdxLicenseList.from_file(config.licenses)
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
    logging.debug(
        "Loading repository from '{0}'...".format(project_config.repository),
    )
    try:
        repository = Repository.create(project_config.repository)
    except (ValidationError, ValueError) as repository_error:
        logging.error(
            "Failed to load repository from '{0}':\n{1}".format(
                project_config.repository, repository_error,
            ),
        )
        continue

    logging.info(
        "Loading manifest from '{0}'...".format(repository.url),
    )
    try:
        manifest = Manifest.from_repository(repository)
    except (ValidationError, ValueError) as manifest_error:
        logging.error(
            "Failed to load manifest from '{0}':\n{1}".format(
                repository.url, manifest_error,
            ),
        )
        continue

    logging.info(
        "Loading description from '{0}'...".format(manifest.description),
    )
    try:
        description = Description.from_url(manifest.description)
    except (ValidationError, ValueError) as description_error:
        logging.error(
            "Failed to load description from '{0}':\n{1}".format(
                repository.url, description_error,
            ),
        )
        continue

    logging.info("Loading licenses for '{0}'...".format(manifest.name))
    licenses = []
    try:
        for license_id in manifest.licenses:
            licenses.append(spdx_licenses.get_license(license_id))
    except (ValidationError, ValueError) as license_error:
        logging.error(
            "Failed to load licenses for '{0}':\n{1}".format(
                manifest.name, license_error,
            ),
        )
        continue

    logging.info("Generating content for '{0}'...".format(manifest.name))
    try:
        project = Project(
            title=manifest.name,
            images=manifest.images,
            categories=project_config.categories,
            featured=project_config.featured,
            website=manifest.website,
            latest_release=manifest.latest_release,
            documentation=manifest.documentation,
            repository=repository.url,
            issues=manifest.issues,
            forum=manifest.forum,
            links=manifest.links,
            contact=project_config.contact,
            licenses=licenses,
            description=description.data,
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
            projects_dir, '{0}.md'.format(repository.project),
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
    try:
        project.dump(project_path)
    except ValidationError as project_dump_error:
        logging.error(
            "Failed to write content for '{0}' to '{1}':\n{2}".format(
                manifest.name, project_path, project_dump_error,
            ),
        )
