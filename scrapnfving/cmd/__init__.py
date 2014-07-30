# Copyright (c) 2014 Red Hat.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

from oslo.config import cfg

from scrapnfving import journaling
from scrapnfving.openstack.common import log as logging
from scrapnfving import scraping
from scrapnfving import sketching

CONF = cfg.CONF
opts = [
    cfg.StrOpt('wiki_url', default='https://wiki.openstack.org/wiki/Teams/NFV',
               help='Wiki URL to scrap from'),
    cfg.StrOpt('dashboard_name', default='nfv.dash',
               help='Defined dashboard file'),
    cfg.BoolOpt('shorten', default=True,
                help='Shorten the result URL or not'),
]

CONF.register_cli_opts(opts)

LOG = logging.getLogger(__name__)

_LOG_SETUP = False


def prepare_logger():
    global _LOG_SETUP

    if not _LOG_SETUP:
        cfg.set_defaults(logging.log_opts,
                         default_log_levels=['scrapnfving=INFO',
                                             ])
        logging.setup('scrapnfving')
        _LOG_SETUP = True


def main():
    prepare_logger()
    cfg.CONF(sys.argv[1:], project='scrapnfving', prog='main')
    dash_file = CONF.find_file(CONF.dashboard_name)
    if not dash_file:
        raise cfg.ConfigFilesNotFoundError((CONF.dashboard_name,))

    scraper = scraping.Scraper(url=CONF.wiki_url)
    urls = scraper.scrap()
    sketcher = sketching.Sketcher()
    reviews = sketcher.sketch(urls)
    journaler = journaling.Journaler()
    gerrit_url = journaler.journal(reviews=reviews,
                                   dash=dash_file)
    LOG.info("URL: %s" % gerrit_url)

if __name__ == '__main__':
    sys.exit(main())
