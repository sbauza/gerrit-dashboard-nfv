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

from oslo.config import cfg

from scrapnfving.utils import gerritdash
from scrapnfving.utils import shorteningservice

CONF = cfg.CONF

opts = [
    cfg.StrOpt('short_url',
               default='http://tiny.cc/fipdix',
               help='Short URL to update'),
]

CONF.register_opts(opts, 'shortening')


class Journaler(object):

    def __init__(self, shorten):
        self.shorten = shorten
        if self.shorten:
            self.shorter = shorteningservice.ShorteningService()

    def journal(self, reviews, dash):
        extra_foreach = ' (%s)' % ' OR '.join(reviews)
        dash_url = gerritdash.gerrit_dashboard(dash,
                                               extra_foreach=extra_foreach)

        print dash_url
        if self.shorten:
            dash_url = self.shorter.update(CONF.shortening.short_url, dash_url)
        return dash_url
