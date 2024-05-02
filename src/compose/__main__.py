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
from news import Newsfeed
from pydantic import ValidationError
from repository import Repository

from hugo import Project

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
    logging.error('Failed to load configuration:\n{0}'.format(config_error))
    sys.exit(1)

logging.info("Loading SPDX license list from '{0}'...".format(config.licenses))
try:
    spdx_licenses = SpdxLicenseList.from_file(config.licenses)
except (ValidationError, ValueError) as spdx_error:
    logging.error('Failed to load SPDX license list:\n{0}'.format(spdx_error))
    sys.exit(1)

for category in config.categories:
    logging.info('{0} - Generating category...'.format(category.name))
    try:
        category.dump(config.sources)
    except (ValidationError, ValueError) as category_error:
        logging.error('{0} - Failed to generate category:\n{1}'.format(
            category.name, category_error,
        ))
        sys.exit(1)

projects_dir = os.path.join(config.sources, 'content/projects')
try:
    os.makedirs(projects_dir)
except OSError as projects_dir_error:
    logging.error("Failed to create '{0}' directory:\n{1}".format(
        projects_dir, projects_dir_error,
    ))
    sys.exit(1)

news_dir = os.path.join(config.sources, 'content/news')
try:
    os.makedirs(news_dir)
except OSError as news_dir_error:
    logging.error("Failed to create '{0}' directory:\n{1}".format(
        news_dir, news_dir_error,
    ))
    sys.exit(1)

for project_config in config.projects:
    try:
        repository = Repository.create(project_config.repository)
    except (ValidationError, ValueError) as repository_error:
        logging.error("Failed to load repository from '{0}':\n{1}".format(
            project_config.repository, repository_error,
        ))
        continue

    logging.info("{0} - Loading manifest from '{1}'...".format(
        repository.project, repository.url,
    ))
    try:
        manifest = Manifest.from_repository(repository)
    except (ValidationError, ValueError) as manifest_error:
        logging.error("{0} - Failed to load manifest from '{1}':\n{2}".format(
            repository.project, repository.url, manifest_error,
        ))
        continue

    logging.info("{0} - Loading description from '{1}'...".format(
        repository.project, manifest.description,
    ))
    try:
        description = Description.from_url(manifest.description)
    except (ValidationError, ValueError) as description_error:
        logging.error(
            "{0} - Failed to load description from '{1}':\n{2}".format(
                repository.project, manifest.description, description_error,
            ),
        )
        continue

    logging.info('{0} - Loading licenses...'.format(repository.project))
    licenses = []
    try:
        for license_id in manifest.licenses:
            licenses.append(spdx_licenses.get_license(license_id))
    except (ValidationError, ValueError) as license_error:
        logging.error('{0} - Failed to load licenses:\n{1}'.format(
            repository.project, license_error,
        ))
        continue

    logging.info('{0} - Generating project page content...'.format(
        repository.project,
    ))
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
            '{0} - Failed to generate project page content:\n{1}'.format(
                repository.project, project_error,
            ),
        )
        continue

    project_path = os.path.join(projects_dir, '{0}.md'.format(
        repository.project,
    ))

    logging.info("{0} - Writing project page content to '{1}'...".format(
        repository.project, project_path,
    ))
    try:
        project.dump(project_path)
    except ValidationError as project_dump_error:
        logging.error(
            "{0} - Failed to write project page content to '{1}':\n{2}".format(
                repository.project, project_path, project_dump_error,
            ),
        )
        continue

    if manifest.newsfeed:
        logging.info('{0} - Loading newsfeed...'.format(repository.project))
        try:
            newsfeed = Newsfeed.from_url(
                url=manifest.newsfeed, project=repository.project,
            )
        except (ValidationError, ValueError) as newsfeed_error:
            logging.error('{0} - Failed to load newsfeed:\n{1}'.format(
                repository.project, newsfeed_error,
            ))
            continue

        logging.info('{0} - Generating news...'.format(repository.project))
        try:
            newsfeed.dump(news_dir)
        except (ValidationError, ValueError) as news_error:
            logging.error('{0} - Failed to generate news:\n{1}'.format(
                repository.project, news_error,
            ))
