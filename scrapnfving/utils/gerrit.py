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
from six.moves import urllib

from scrapnfving.openstack.common import excutils
from scrapnfving.openstack.common import jsonutils

CONF = cfg.CONF

opts = [
    cfg.StrOpt('url',
               default='https://review.openstack.org/',
               help='Gerrit API URL'),
]

CONF.register_opts(opts, 'gerrit')


class GerritAPI(object):

    def _request(self, path):
        """ Performs HTTP POST call.

        :returns: HTTP response body
        """
        url = urllib.parse.urljoin(CONF.gerrit.url, path)
        request = urllib.request.Request(url)
        try:
            sock = urllib.request.urlopen(request)
            response = sock.read()
        except Exception:
            with excutils.save_and_reraise_exception():
                raise Exception(
                    'Your URL %s is incorrect, please check.' % url)
        return response

    def get_changes(self, query):
        qs = urllib.parse.quote_plus(query, ':()%')
        response = self._request(path='/changes/?q=%s&o=LABELS' % qs)
        #NOTE: JSON response from Gerrit is malformed
        response = response.split('\n', 1)[1]
        try:
            changes = jsonutils.loads(response)
        except ValueError:
            with excutils.save_and_reraise_exception():
                raise Exception("Unable to get changes from Gerrit from \n"
                                "%s" % response)
        return changes

    def get_search_url(self, query):
        qs = urllib.parse.quote_plus(query, ':()')
        return urllib.parse.urljoin(CONF.gerrit.url, '/#/q/%s,n,z' % qs)

    def get_account(self, account_id):
        response = self._request(path='/accounts/%s/name' % account_id)
        #NOTE: JSON response from Gerrit is malformed
        response = response.split('\n', 1)[1]
        # Returned value has a leading/trailing quote to drop
        return response[1:-2]
