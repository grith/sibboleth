#############################################################################
#
# Copyright (c) 2011 Russell Sim <russell.sim@gmail.com> Contributors.
# Copyright (c) 2009 Victorian Partnership for Advanced Computing Ltd and
# Contributors.
# All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from HTMLParser import HTMLParser


class FormParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.in_title = False
        self.in_form = False
        self.in_wayf = False
        self.in_ds = False
        self.ds_optgroup = ''
        self.title = ''
        self.forms = []
        self.data = {}

    def handle_starttag(self, tag, attrs):
        self.origin_idp = None
        self.ds_idp = None
        if tag == "title":
            self.in_title = True
        if tag == "form":
            if self.data:
                self.data = {}
            self.in_form = True
            self.data['form'] = dict(attrs)
        if self.in_form and tag == "select" and ('name', 'origin') in attrs:
            self.in_wayf = True
            self.data['origin'] = {}
        if self.in_form and tag == "select" and ('name', "user_idp") in attrs:
            self.in_ds = True
            self.data['ds'] = {}
        if self.in_form and self.in_ds and tag == "optgroup":
            self.ds_optgroup = dict(attrs)['label']
            self.data['ds'][self.ds_optgroup] = {}
        if self.in_form and self.in_ds and tag == "option":
            origin_idp = dict(attrs)
            if not origin_idp['value'] in ['-', '']:
                self.origin_idp = origin_idp['value']

        if self.in_form and self.in_wayf and tag == "option":
            self.origin_idp = attrs
        if self.in_form and tag == "input":
            attrs = dict(attrs)
            if 'name' in attrs:
                self.data[attrs['name']] = attrs

    def handle_data(self, data):
        if self.in_form and self.in_wayf and self.origin_idp and data.strip():
            self.data['origin'][data.strip()] = self.origin_idp[0][1]
        if self.in_form and self.in_ds and self.origin_idp and data.strip():
            self.data['ds'][self.ds_optgroup][data.strip()] = self.origin_idp
        if self.in_title:
            self.title += data

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "form":
            self.in_form = False
            self.forms.append(self.data)
        if self.in_form and self.in_wayf and tag == "select":
            self.in_wayf = False
        if self.in_form and self.in_ds and tag == "optgroup":
            self.ds_optgroup = ''
        if self.in_form and self.in_ds and tag == "select":
            self.in_ds = False


def html_parser(html):
    parser = FormParser()
    for line in html:
        parser.feed(line)
    parser.close()
    return None, parser.title, parser.forms
