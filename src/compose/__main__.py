# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""CLI to generate content for ohwr.org."""

import argparse
import json
import logging
from urllib.request import urlopen

import config
import yaml
from sources import ProjSources

parser = argparse.ArgumentParser()
parser.add_argument('config', type=argparse.FileType('r'))
args = parser.parse_args()

local_config = yaml.safe_load(args.config)

logging.basicConfig(
    level=getattr(logging, local_config['log_level']),
    format='%(asctime)s - %(levelname)s - %(message)s',  # noqa: WPS323
)

with urlopen(local_config['license_list']) as response:  # noqa: S310
    spdx_license_list = json.load(response)

for proj in local_config['projects']:
    try:
        proj_config = config.Project.from_url(
            spdx_license_list=spdx_license_list,
            **proj,
        )
    except config.ConfigError as error:
        msg = 'Could not configure the {0} project:\n↳ {1}'
        logging.error(msg.format(proj['id'], error))
        continue
    proj_sources = ProjSources.from_config(proj_config)
    proj_sources.dump(local_config['source'])
