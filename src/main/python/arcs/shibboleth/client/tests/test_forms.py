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
from arcs.shibboleth.client import shibboleth, forms
import inspect

from os import path
here = path.join(path.dirname(inspect.getsourcefile(shibboleth)), 'tests/')
class TestShibboleth(unittest.TestCase):

    def setUp(self):
        pass

    def testFormAdapterDetection(self):
        for i in ['wayf_level1', 'login_vpac', 'cas_login_jcu', 'login_ac3', 'login_uq', 'cas_login_usa', 'ds_aaf']:
            type, name = i.rsplit('_', 1)
            html = open(path.join(here, i + '.html'))
            parser = shibboleth.FormParser()
            for line in html:
                parser.feed(line)
            parser.close()
            rname, adapter = forms.getFormAdapter(parser.title, parser.forms, None, None)
            self.assertEqual('_'.join([rname, name]), i)


if __name__ == '__main__':
    unittest.main()


