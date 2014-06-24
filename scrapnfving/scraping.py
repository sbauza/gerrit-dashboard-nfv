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

from six.moves import urllib
from six.moves import html_parser

from oslo.config import cfg

CONF = cfg.CONF

opts = [
    cfg.BoolOpt('strict', default=False,
                help='Strict HTML parsing'),
    cfg.StrOpt('th_name', default='Blueprint(s)',
               help='Column name for wikitables containing blueprints')
]

CONF.register_opts(opts, 'parser')


# NOTE(sbauza): HTMLParser is old-style in Py2
class Scraper(html_parser.HTMLParser, object):
    def __init__(self, url=None):
        if isinstance(html_parser.HTMLParser, type):
            super(Scraper, self).__init__(strict=CONF.parser.strict)
        else:
            # strict is not supported for HTMLParser in Py2
            super(Scraper, self).__init__()
        # TODO caching
        # TODO stream detection and validation
        try:
            sock = urllib.request.urlopen(url)
            self.htmlSource = sock.read()
        except Exception:
            raise Exception('Your URL %s is incorrect, please check.' % url)
        self.urls = set()

        # Internals for parsing
        self._inth = False
        self._th_offset = 0
        self._intd = False
        self._td_offset = 0
        self._marker_pos = 0

    def scrap(self):
        self.marker = CONF.parser.th_name
        self.feed(self.htmlSource)
        return self.urls

    def handle_starttag(self, tag, attrs):
        if tag == 'th':
            self._th_offset += 1
            self._inth = True
        if tag == 'td':
            self._td_offset += 1
            self._intd = True
        if tag == 'a' and self._intd:
            if self._marker_pos != 0 and self._marker_pos == self._td_offset:
                # There is only one href attribute
                url = [value for (name, value) in attrs if name == 'href'][0]
                self.urls.add(url)

    def handle_endtag(self, tag):
        if tag == 'th':
            self._inth = False
        if tag == 'td':
            self._intd = False
        if tag == 'tr':
            # The row is ended to read
            self._th_offset = 0
            self._td_offset = 0
        if tag == 'tbody':
            # Reset marker position, we're out of the wikitable
            self._marker_pos = 0

    def handle_data(self, data):
        if self._inth:
            if data.strip() == self.marker:
                self._marker_pos = self._th_offset
