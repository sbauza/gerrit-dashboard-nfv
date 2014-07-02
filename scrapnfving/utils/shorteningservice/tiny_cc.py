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

"""Tiny.cc plugin."""

import copy
import json

from oslo.config import cfg

from scrapnfving.utils.shorteningservice import base

CONF = cfg.CONF

opts = [
    cfg.StrOpt('login',
               default='mylogin',
               help='Tiny.cc login'),
    cfg.StrOpt('apikey',
               default='mysecretapikey',
               secret=True,
               help='Tiny.cc API key (see http://tiny.cc/api-docs)'),
    cfg.StrOpt('version',
               default='2.0.3',
               help='Tiny.cc API version (see http://tiny.cc/api-docs)'),
    cfg.StrOpt('hash',
               default=None,
               help='Tiny.cc Short URL hash (see http://tiny.cc/api-docs)'),
]

CONF.register_opts(opts, 'tiny_cc')


class TinyCCPlugin(base.BasePlugin):

    url_root = 'http://tiny.cc/'

    params = {'c': 'rest_api',
              'login': CONF.tiny_cc.login,
              'apiKey': CONF.tiny_cc.apikey,
              'version': CONF.tiny_cc.version,
              'format': 'json'}

    _hashes = dict()

    def authenticate(self):
        # NOTE(sbauza): Not necessary, Tiny.cc API doesn't support OAuth
        pass

    def shorten(self, long_url):
        """ Shorten a long URL.

        :returns: a short url
        """
        params = copy.deepcopy(self.params)
        params.update({'m': 'shorten'})
        params.update({'longUrl': long_url})
        res = self._request(self.url_root, params)
        print "Short URL hash : %s" % self._hashes[res]
        return res

    def update(self, short_url, long_url):
        urlhash = self._hashes.get(short_url, CONF.tiny_cc.hash)
        if not urlhash:
            print "WARNING: Hash not existing, creating another short url."
            return self.shorten(long_url)
        else:
            # NOTE(sbauza): Short URL needs to only be the path
            short_url = short_url.replace(self.url_root, '')
            params = copy.deepcopy(self.params)
            params.update({'m': 'edit'})
            params.update({'longUrl': long_url})
            params.update({'shortUrl': short_url})
            params.update({'hash': urlhash})
            params.update({'userHash': urlhash})

            return self._request(self.url_root, params)

    def _request(self, url, params):
        json_response = self.request(url, params)
        response = json.loads(json_response)

        print response
        if response['errorCode'] == '0' and response['statusCode'] == 'OK':
            # Cool...
            self._hashes.update(
                {response['results']['short_url']:
                    response['results']['hash']})
            return response['results']['short_url']
