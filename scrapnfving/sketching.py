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

import re

from oslo.config import cfg

from scrapnfving.utils import launchpad

CONF = cfg.CONF

opts = [
    cfg.StrOpt('pattern_reviews',
               default="http[s]?://review.openstack.org/(?:#/c/)?([0-9]+)",
               help='Regex pattern for searching review topics')
]

CONF.register_opts(opts, 'gerrit')


class Sketcher(object):
    def __init__(self):
        self.lp = launchpad.LaunchpadConnection(anon=True)
        # NOTE(sbauza): We can also track Gerrit topics but they are less
        #               relevant because of some typos in topic names
        self.re_reviews = re.compile(CONF.gerrit.pattern_reviews)
        self.reviews = set()

    def sketch(self, urls):
        for url in urls:
            bp_wb = self.lp.get_bp_whiteboard(url)
            if bp_wb:
                self.reviews.update(self.re_reviews.findall(bp_wb))
        return self.reviews
