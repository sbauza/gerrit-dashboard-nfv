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


def main():
    cfg.CONF(sys.argv[1:], project='scrapnfving', prog='main')
    # TODO(sbauza): Pecan WSGI app

if __name__ == '__main__':
    sys.exit(main())
