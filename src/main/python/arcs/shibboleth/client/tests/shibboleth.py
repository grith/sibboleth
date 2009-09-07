#############################################################################
#
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
from arcs.shibboleth.client import shibboleth
import inspect

from os import path
here = path.join(path.dirname(inspect.getsourcefile(shibboleth)), 'tests/')
class TestShibboleth(unittest.TestCase):

    def setUp(self):
        pass

    def testFormTypeDetection(self):
        for i in ['wayf_level1', 'login_vpac', 'login_jcu', 'login_ac3', 'login_auckland', 'login_murdoch', 'login_uq', 'login_usa']:
            type, name = i.split('_')
            html = open(path.join(here, i + '.html'))
            parser = shibboleth.FormParser()
            for line in html:
                parser.feed(line)
            parser.close()
            rtype, form = shibboleth.whatForm(parser.forms)
            self.assertEqual('_'.join([rtype, name]), i)


if __name__ == '__main__':
    unittest.main()


