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

import abc

import six
from six.moves import urllib


@six.add_metaclass(abc.ABCMeta)
class BasePlugin(object):

    # URL Root for accessing the API
    url_root = None

    # Authentication key set by authenticate()
    auth_key = None

    @abc.abstractmethod
    def authenticate(self):
        """ Define remote authentication for the service (OAuth, etc.).

        :returns: authenticated token
        """
        pass

    @abc.abstractmethod
    def shorten(self, long_url):
        """ Shorten a long URL.

        :returns: a short url
        """
        pass

    @abc.abstractmethod
    def update(self, short_url, long_url):
        """ Update an existing short URL with a new long URL.

        :returns: a short url
        """
        pass

    def request(self, url, params, method='GET'):
        """ Performs HTTP POST call.

        :returns: HTTP response body
        """
        data = urllib.parse.urlencode(params)
        if method == 'GET':
            # Ugly hack...
            url = url+'?'+data
            data = None
        print "DEB: %s" % url
        request = urllib.request.Request(url)
        if method == 'POST':
            request.add_header(
                "Content-Type",
                "application/x-www-form-urlencoded;charset=utf-8")
        try:
            sock = urllib.request.urlopen(request)
            # response = sock.read().decode('utf-8')
            response = sock.read()
        except Exception:
            raise Exception('Your URL %s is incorrect, please check.' % url)
        return response
