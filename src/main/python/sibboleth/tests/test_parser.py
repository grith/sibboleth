#############################################################################
#
# Copyright (c) 2011 Russell Sim <russell.sim@gmail.com> and Contributors.
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

import unittest
import inspect

from sibboleth import shibboleth
from sibboleth.parsers.htmlparser import html_parser
from sibboleth.parsers.lxmlhtml import lxml_parser
from sibboleth.parsers.soup import soup_parser

from os import path
here = path.join(path.dirname(inspect.getsourcefile(shibboleth)), 'tests/')


class TestHTMLParser(unittest.TestCase):
    """This series of test is trying test the parsers to confirm the
    data they return"""
    def setUp(self):
        self.parser = html_parser

    def testDecoding(self):
        parser = self.parser
        f = open(path.join(here, 'encoded.html'))
        self.assertEqual(
            [{'SAMLResponse':
              {'type': 'hidden', 'name': 'SAMLResponse',
               'value': 'dGVzdA=='},
              'RelayState':
              {'type': 'hidden', 'name': 'RelayState',
               'value': u'cookie:58a2faee'},
              'form':
              {'action': u'https://slcstest.arcs.org.au/' \
                    'Shibboleth.sso/SAML2/POST',
               'method': 'post'},
              'submit': {u'type': u'submit',
                         u'value': u'Continue'}}],
            parser(f)[2])


class TestLXMLParser(TestHTMLParser):
    """This series of test is trying test the parsers to confirm the
    data they return"""
    def setUp(self):
        self.parser = lxml_parser


class TestSoupParser(TestHTMLParser):
    """This series of test is trying test the parsers to confirm the
    data they return"""
    def setUp(self):
        self.parser = soup_parser
