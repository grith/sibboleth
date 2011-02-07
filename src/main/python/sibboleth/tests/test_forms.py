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

import unittest
from sibboleth import shibboleth, forms
import inspect

from os import path
here = path.join(path.dirname(inspect.getsourcefile(shibboleth)), 'tests/')


class TestForms(unittest.TestCase):

    def setUp(self):
        pass

    def _formadapter(self, file_name):
        type, name = file_name.rsplit('_', 1)
        html = open(path.join(here, file_name + '.html'))

        rname, adapter = forms.getFormAdapter(html, None, None)
        self.assertEqual('_'.join([rname, name]), file_name)

    def testWAYF(self):
        self._formadapter('wayf_level1')

    def testIDP(self):
        self._formadapter('login_vpac')
        self._formadapter('login_ac3')
        self._formadapter('login_uq')
        # TODO make the unittest below pass
        #self._formadapter('login_murdoch')

    def testCAS(self):
        self._formadapter('cas_login_jcu')
        self._formadapter('cas_login_usa')

    def testDS(self):
        self._formadapter('ds_aaf')
        self._formadapter('ds_aafnew')

    def testESOE(self):
        self._formadapter('esoe_chooser')
        self._formadapter('esoe_login_qut')

    def testCOSIGN(self):
        self._formadapter('cosign_login_auckland')

    def testCASRedirect(self):
        self._formadapter('cas_redirect_jcu')
