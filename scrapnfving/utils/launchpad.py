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

"""Set of tools for connecting to Launchpad."""

from os import path

from launchpadlib import launchpad
from oslo.config import cfg
from six.moves import urllib

CONF = cfg.CONF

opts = [
    cfg.StrOpt('client',
               default='just testing',
               help='Launchpad client name'),
    cfg.StrOpt('instance',
               default='production',
               help='Launchpad webservice instance'),
    cfg.StrOpt('api_version',
               default='devel',
               help='Version of the LaunchpadAPI'),
]

CONF.register_opts(opts, 'launchpad')


class LaunchpadConnection(object):
    def __init__(self, anon=True):
        self.lp = connectLaunchpad(anon)

    def _get_blueprint(self, url):
        spec = urllib.parse.urlparse(url)[2]
        if spec:
            spec_path = spec.split('/')
            if spec_path[2] == '+spec':
                (project, bp_title) = (spec_path[1], spec_path[3])

        try:
            return self.lp.projects[project].getSpecification(name=bp_title)
        except Exception:
            raise Exception("URL %s is not a blueprint" % url)

    def get_blueprint(self, url):
        return str(self._get_blueprint(url))

    def get_bp_whiteboard(self, url):
        bp = self._get_blueprint(url)
        if bp:
            return getattr(bp, 'whiteboard')
        else:
            print "ERROR: %s is not a blueprint" % url
            return None


def connectLaunchpad(anonymously=True):
    """
    Connect to Launchpad.

    :param anonymously: Connect without credentials

    :returns: a launchpad connection object
    """

    if anonymously:
        cachedir = "%s/.launchpadlib/cache/" % path.expanduser("~")
        return launchpad.Launchpad.login_anonymously(
            CONF.launchpad.client,
            CONF.launchpad.instance,
            cachedir,
            version=CONF.launchpad.api_version)
    else:
        raise NotImplementedError
