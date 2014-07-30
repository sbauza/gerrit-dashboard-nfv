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

import eventlet
eventlet.monkey_patch()
from oslo.config import cfg

from scrapnfving import cmd as main_cmd
from scrapnfving.openstack.common import excutils
from scrapnfving.openstack.common import log as logging
from scrapnfving.openstack.common import service

CONF = cfg.CONF
opts = [
    cfg.IntOpt('update_period', default=3600,
               help='Period in between 2 updates (in secs)'),
]

CONF.register_cli_opts(opts)

LOG = logging.getLogger(__name__)


class Engine(service.Service):

    def start(self):
        self.tg.add_timer(CONF.update_period, self.scrap)

    def scrap(self):
        try:
            main_cmd.main()
        except Exception:
            with excutils.save_and_reraise_exception():
                LOG.error("An Exception occurred")
                sys.exit(1)


def main():
    cfg.CONF(sys.argv[1:], project='scrapnfving', prog='engine')
    main_cmd.prepare_logger()

    service.launch(
        Engine()
    ).wait()


if __name__ == '__main__':
    sys.exit(main())
