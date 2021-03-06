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

"""Shamely copied/adapted from stackforge/gerrit-dash-creator."""

import fileinput
import re

from six.moves import urllib


def _escape_comma(buff):
    """Because otherwise Firefox is a sad panda."""
    return buff.replace(',', '%2c')


def _get_title(fname):
    title = ""
    foreach = ""
    for line in fileinput.input(fname):
        m = re.match("title = (.+)", line)
        if m:
            title = m.group(1)

        m = re.match("foreach = (.+)", line)
        if m:
            foreach = _escape_comma(m.group(1))
    fileinput.close()
    return title, foreach


def _get_sections(fname, extra_foreach=None):
    sections = []
    sname = None
    for line in fileinput.input(fname):
        m = re.match('\[section "([^"]+)', line)
        if m:
            sname = m.group(1)
        elif sname:
            m = re.match("query = (.+)", line)
            if m:
                query = _escape_comma(m.group(1))
                if extra_foreach:
                    query += extra_foreach
                sections.append({'title': sname, 'query': query})
    fileinput.close()
    return sections


def _gen_url(title, foreach, sections):
    base = 'https://review.openstack.org/#/dashboard/?'
    base += urllib.parse.urlencode({'title': title, 'foreach': foreach})
    base += '&'
    encoded = [urllib.parse.urlencode(
        {x['title']: x['query']}) for x in sections]
    base += '&'.join(encoded)
    return base


def gerrit_dashboard(dash, extra_foreach=None):
    """Generates a custom Gerrit dashboard.

    :param dash: path of the custom defined dashboard file
    :param extra_foreach: extra search parameters for the dashboard
    :returns: a long URL string
    """
    title, foreach = _get_title(dash)
    if extra_foreach:
        foreach += extra_foreach
    sections = _get_sections(dash)
    url = _gen_url(title, foreach, sections)
    return url


def dashboard(dash, extra_foreach=None):
    title, foreach = _get_title(dash)
    sections = _get_sections(dash, extra_foreach)
    return (title, sections)
