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

from scrapnfving.utils import gerritdash

CONF = cfg.CONF

opts = [
    cfg.StrOpt('matching_reviews',
               default="http[s]?://review.openstack.org/([0-9]+)",
               help='Regex pattern for extracting review IDs')
]

CONF.register_opts(opts, 'gerrit')


def journal(review_urls, dash):
    dash_file = CONF.find_file(dash)
    if not dash_file:
        raise cfg.ConfigFilesNotFoundError((dash,))
    re_reviews_ids = re.compile(CONF.gerrit.matching_reviews)
    reviews = []
    for review_url in review_urls:
        m = re_reviews_ids.match(review_url)
        if m:
            reviews.append(m.group(1))
    extra_foreach = ' (%s)' % ' OR '.join(reviews)
    return gerritdash.gerrit_dashboard(dash_file, extra_foreach=extra_foreach)
