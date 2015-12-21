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

import datetime
import os

import jinja2
from oslo.config import cfg

from scrapnfving.openstack.common import timeutils
from scrapnfving.utils import gerrit
from scrapnfving.utils import gerritdash

CONF = cfg.CONF

opts = [
    cfg.StrOpt('file',
               default='/var/www/html/dashboard.html',
               help='Page to update'),
    cfg.StrOpt('template',
               default='index.html.jinja2',
               help='Jinja2 template for generating the page'),
]

CONF.register_opts(opts, 'journal')

CONF.import_opt('url', 'scrapnfving.utils.gerrit', 'gerrit')


class Journaler(object):

    def __init__(self):
        self.gerrit_api = gerrit.GerritAPI()
        template_file = CONF.find_file(CONF.journal.template)
        template_path, template_name = os.path.split(template_file)
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
        self.template = env.get_template(template_name)

    def journal(self, reviews, dash):
        extra_foreach = ' (%s)' % ' OR '.join(reviews)
        (dash_title, sections) = gerritdash.dashboard(dash, extra_foreach)
        for section in sections:
            query = section.pop('query')
            changes = self.gerrit_api.get_changes(query)
            section['reviews'] = [self.change_to_review(change)
                                  for change in changes]
            section['url'] = self.gerrit_api.get_search_url(query)
        self.generate_dashboard(dash_title, sections)

    def generate_dashboard(self, title, sections):
        with open(CONF.journal.file, 'w+') as fp:
            fp.write(self.template.render(title=title, sections=sections)
                     .encode('utf-8'))

    def change_to_review(self, change):
        review = {}
        review['subject'] = change['subject'] if len(change['subject']) <= 72 \
            else change['subject'][:72] + '...'
        review['owner'] = self.gerrit_api.get_account(change['owner']['_account_id'])
        review['owner_url'] = self.gerrit_api.get_search_url(
            'owner:"'+str(change['owner']['_account_id'])+'" status:open')
        review['project'] = change['project']
        topic = " (%s)" % change['topic'] if 'topic' in change else ''
        review['branch'] = "%(b)s%(t)s" % {'b': change['branch'],
                                           't': topic}
        branch_url = 'status:open project:'+change['project']+''
        ' branch:'+change['branch']+''
        if 'topic' in change:
            branch_url += ' topic:'+change.get('topic')
        review['branch_url'] = self.gerrit_api.get_search_url(branch_url)
        updated = timeutils.normalize_time(
            timeutils.parse_isotime(change['updated']))
        if updated >= datetime.datetime.combine(timeutils.utcnow(),
                                                datetime.time(0, 0, 0)):
            review['updated'] = updated.strftime("%-I:%M %p")
        else:
            review['updated'] = updated.strftime("%b %-d")

        if 'Code-Review' in change['labels']:
            cr = change['labels']['Code-Review']
            if cr.get('rejected'):
                review['code-review'] = "-2"
                review['cr_note'] = "negscore"
            elif cr.get('approved'):
                review['code-review'] = "+2"
                review['cr_note'] = "posscore"
            elif cr.get('disliked'):
                review['code-review'] = "-1"
                review['cr_note'] = "negscore"
            elif cr.get('recommended'):
                review['code-review'] = "+1"
                review['cr_note'] = "posscore"

        if 'Verified' in change['labels']:
            cr = change['labels']['Verified']
            if cr.get('rejected'):
                review['verified'] = "-2"
                review['v_note'] = "negscore"
            elif cr.get('approved'):
                review['verified'] = "+2"
                review['v_note'] = "posscore"
            elif cr.get('disliked'):
                review['verified'] = "-1"
                review['v_note'] = "negscore"
            elif cr.get('recommended'):
                review['verified'] = "+1"
                review['v_note'] = "posscore"

        if 'Workflow' in change['labels']:
            cr = change['labels']['Workflow']
            if cr.get('rejected'):
                review['workflow'] = "-2"
                review['w_note'] = "negscore"
            elif cr.get('approved'):
                review['workflow'] = "+2"
                review['w_note'] = "posscore"
            elif cr.get('disliked'):
                review['workflow'] = "-1"
                review['w_note'] = "negscore"
            elif cr.get('recommended'):
                review['workflow'] = "+1"
                review['w_note'] = "posscore"

        review['url'] = self.gerrit_api.get_search_url(str(change['_number']))
        return review
