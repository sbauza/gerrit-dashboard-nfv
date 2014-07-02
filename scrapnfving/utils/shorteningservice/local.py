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

"""Local file plugin."""

import os

import jinja2
from oslo.config import cfg

from scrapnfving.utils.shorteningservice import base

CONF = cfg.CONF

opts = [
    cfg.StrOpt('file',
               default='/var/www/html/index.html',
               help='Page to update'),
    cfg.StrOpt('template',
               default='index.html.jinja2',
               help='Jinja2 template for generating the page'),
]

CONF.register_opts(opts, 'local_file')


class LocalFilePlugin(base.BasePlugin):

    def authenticate(self):
        # NOTE(sbauza): Not necessary, Tiny.cc API doesn't support OAuth
        pass

    def shorten(self, long_url):
        pass

    def update(self, short_url, long_url):
        template_file = CONF.find_file(CONF.local_file.template)

        template_path, template_name = os.path.split(template_file)
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
        template = env.get_template(template_name)

        with open(CONF.local_file.file, 'w+') as fp:
            fp.write(template.render(url=long_url))

        return CONF.local_file.file
