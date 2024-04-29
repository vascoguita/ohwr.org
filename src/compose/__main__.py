# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Generate content for ohwr.org."""

import argparse
import logging
import os
import sys

from config import Config
from content import Category, News, Project
from description import Description
from license import SpdxLicenseList
from manifest import Manifest
from news import NewsList
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
except (ValidationError, ValueError) as spdx_error:
    logging.error(
        'Failed to load SPDX license list:\n{0}'.format(spdx_error),
    )
    sys.exit(1)

if config.categories:
    for category_config in config.categories:
        logging.debug(
            "Defining category directory for '{0}'...".format(
                category_config.name,
            ),
        )
        try:
            category_dir = os.path.join(
                config.sources,
                'content/categories',
                category_config.name.lower().replace(' ', '-'),
            )
        except (TypeError, AttributeError, BytesWarning) as category_dir_error:
            logging.error(
                "Failed to define category directory for '{0}':\n{1}".format(
                    category_dir_error, category_config.name,
                ),
            )
            sys.exit(1)

        logging.debug("Creating '{0}' directory...".format(category_dir))
        try:
            os.makedirs(category_dir)
        except OSError as make_category_dir_error:
            logging.error(
                "Failed to create '{0}' directory:\n{1}".format(
                    category_dir, make_category_dir_error,
                ),
            )
            sys.exit(1)

        logging.info(
            "Generating the '{0}' category...".format(category_config.name),
        )
        try:
            category = Category(
                title=category_config.name,
                description=category_config.description,
            )
        except ValidationError as category_error:
            logging.error(
                "Failed to generate the '{0}' category:\n{1}".format(
                    category_config.name, category_error,
                ),
            )
            sys.exit(1)

        logging.debug(
            "Defining category path for '{0}'...".format(category.title),
        )
        try:
            category_path = os.path.join(category_dir, '_index.md')
        except (
            TypeError, AttributeError, BytesWarning,
        ) as category_path_error:
            logging.error(
                "Failed to define category path for '{0}':\n{1}".format(
                    category.title, category_path_error,
                ),
            )
            sys.exit(1)

        logging.info(
            "Writing category '{0}' to '{1}'...".format(
                category.title, category_path,
            ),
        )
        try:
            category.dump(category_path)
        except ValidationError as category_dump_error:
            logging.error(
                "Failed to write content for '{0}' to '{1}':\n{2}".format(
                    category.title, category_path, category_dump_error,
                ),
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

logging.debug('Defining content directory for news...')
try:
    news_dir = os.path.join(config.sources, 'content/news')
except (TypeError, AttributeError, BytesWarning) as news_dir_error:
    logging.error(
        'Failed to define content directory for news:\n{0}'.format(
            news_dir_error,
        ),
    )
    sys.exit(1)

logging.debug("Creating '{0}' directory...".format(news_dir))
try:
    os.makedirs(news_dir)
except OSError as news_makedirs_error:
    logging.error(
        "Failed to create '{0}' directory:\n{1}".format(
            news_dir, news_makedirs_error,
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

    logging.info("Loading manifest from '{0}'...".format(repository.url))
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
                manifest.description, description_error,
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
        continue

    if manifest.newsfeed:
        logging.info(
            "Loading newsfeed from '{0}'...".format(manifest.newsfeed),
        )
        try:
            news_list = NewsList.from_url(manifest.newsfeed)
        except (ValidationError, ValueError) as newsfeed_error:
            logging.error(
                "Failed to load newsfeed from '{0}':\n{1}".format(
                    manifest.newsfeed, newsfeed_error,
                ),
            )
            continue

        for index, news_item in enumerate(news_list):
            logging.info("Generating news for '{0}'...".format(manifest.name))
            try:
                news = News(
                    title=news_item.title,
                    date=news_item.date,
                    images=news_item.images,
                    topics=[manifest.name],
                    description=news_item.description,
                )
            except ValidationError as news_error:
                logging.error(
                    "Failed to generate news for '{0}':\n{1}".format(
                        manifest.name, news_error,
                    ),
                )
                continue
            logging.debug(
                "Defining path for news '{0}':{1}...".format(
                    manifest.name, index,
                ),
            )
            try:
                news_path = os.path.join(
                    news_dir, '{0}-{1}.md'.format(
                        repository.project, index + 1,
                    ),
                )
            except (TypeError, AttributeError, BytesWarning) as news_path_error:
                logging.error(
                    "Failed to define path for news '{0}':{1}:\n{2}".format(
                        manifest.name, index, news_path_error,
                    ),
                )
                continue
            logging.info(
                "Writing news '{0}':{1} to '{2}'...".format(
                    manifest.name, index, news_path,
                ),
            )
            try:
                news.dump(news_path)
            except ValidationError as news_dump_error:
                logging.error(
                    "Failed to write news '{0}':{1} to '{2}':\n{3}".format(
                        manifest.name, index, news_path, news_dump_error,
                    ),
                )
                continue
