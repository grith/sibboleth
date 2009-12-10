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

import os
from getpass import getpass
import sys

is_jython = sys.platform.startswith('java')

if is_jython:
    from au.org.arcs.auth.shibboleth import CredentialManager as ICredentialManager
    from au.org.arcs.auth.shibboleth import IdpObject as IIdp
else:
    ICredentialManager = object
    IIdp = object


class SimpleCredentialManager(ICredentialManager):
    """
    This class is responsible for authenticating the user in a non interactive way.
    """

    def __init__(self, username, password):
        self.tries = 0
        self.username = username
        self.password = password

    def set_title(self, title):
        """
        show the title of the Basic Auth or Form that the user is presented with.
        """
        pass

    def prompt(self, controller):
        """
        check that we havent tried to authenticate more then once, if we have then raise and exception
        """
        if self.tries < 1:
            controller.run()
        raise Exception("Authentication Failure, number of tries exceeded")

    def get_password(self):
        """return the password of the user"""
        return self.password

    def get_username(self):
        return self.username


class CredentialManager(ICredentialManager):
    """
    This class is responsible for displaying information about the location
    being authed too, and receiving user name and password from the user.
    """

    def __init__(self, username=None, password=None):
        if username:
            self.username = username
        if password:
            self.password = password

    def set_title(self, title):
        """
        show the title of the Basic Auth or Form that the user is presented with.
        """
        print title

    def prompt(self, controller):
        """
        the controller.run() function is called as the last method in this function to return control

        :param controller: the :class:`~arcs.shibboleth.client.shibboleth.Shibboleth` controller that control will be handed back to once the class is finshed taking input
        """
        user_name = os.getenv('USERNAME') or os.getenv('LOGNAME')
        self.username = raw_input("Username [%s]:" % user_name) or user_name
        self.password = getpass("Password:")
        return controller.run()

    def get_password(self):
        """return the password of the user"""
        return self.password

    def get_username(self):
        """return the username of the user"""
        return self.username


class Idp(IIdp):
    """
    This class responds to the WAYF form with the selected idp
    """
    def __init__(self, idp=None):
        self.idp = idp or ''
        self.raw_idps = {}
        self.idps = []

    def set_idps(self, idps):
        """
        set the list of possible idps
        """
        self.raw_idps = idps
        self.idps = idps.keys()
        self.idps.sort()

    def prompt(self, controller):
        """
        some how decide what idp to authenticate to
        the controller.run() function is called as the last method in this function to return control

        :param controller: the :class:`~arcs.shibboleth.client.shibboleth.Shibboleth` controller that control will be handed back to once the class is finshed taking input
        """
        controller = controller
        if self.idp:
            return controller.run()

        try:
            import struct, fcntl, termios
            def terminal_dimensions():
                """return the dimensions of the terminal"""
                fd = os.open(os.ctermid(), os.O_RDONLY)
                if not os.isatty(fd):
                    return (0,0)
                return struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))


            def print_list_wide(items):
                """print the list as columns"""
                lmax = max([len(x) for x in items]) + 1
                width = terminal_dimensions()[1]
                if width:
                    col = width/lmax
                    i = 1
                    for item in items:
                        if not i % col:
                            print item
                        else:
                            print item.ljust(lmax),
                        i = i + 1
                    if i - 1 % col:
                        print('')
                else:
                    for item in items:
                        print item
        except:
            def print_list_wide(items):
                """print the list"""
                for item in items:
                    print item


        idp_list = []
        for n in range(0, len(self.idps)):
            idp_list.append("%s: %s" % (n + 1, self.idps[n]))
        print_list_wide(idp_list)
        idp_n = 0
        while not idp_n - 1 in range(0, len(self.idps)):
            idp_n = int(raw_input("Idp (1-%i):" % (len(self.idps))))
        self.idp = self.idps[idp_n - 1]
        return controller.run()


    def get_idp(self):
        """
        return the selected idp
        """
        return self.idp

