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

class SimpleCredentialManager:
    """
    This class is responsible for displaying information about the location
    being authed too, and receiving user name and password from the user.
    """

    def __init__(self, username, password, printfunc):
        self.username = username
        self.password = password
        self.printfunc = printfunc
        self.tries = 0

    def get_password(self):
        """return the password of the user"""
        return self.password

    def set_password(self, verify=False):
        return self.password

    def set_username(self):
        return self.username

    def get_username(self):
        return self.username

    def reset(self):
        pass

class CredentialManager:
    """
    This class is responsible for displaying information about the location
    being authed too, and receiving user name and password from the user.
    """

    def __init__(self, username=None, password=None, printfunc=None):
        self.username = username
        self.password = password
        self.printfunc = printfunc
        self.tries = 0

    def get_password(self):
        """return the password of the user"""
        if not self.password:
            self.set_password()
        return self.password

    def set_password(self, verify=False):
        if verify:
            while 1:
                p1=getpass('Enter password:')
                p2=getpass('Verify password:')
                if not p1:
                    print "Password cannot be blank"
                    continue
                if p1==p2:
                    self.password = p1
                    break
                print "Password doesn't match"
        else:
            self.password = getpass("Password:")
        return self.password

    def set_username(self):
        if not self.username:
            user_name = os.getenv('USERNAME') or os.getenv('LOGNAME')
            self.username = raw_input("Username [%s]:" % user_name) or user_name
        return self.username

    def get_username(self):
        if not self.username:
            self.set_username()
        return self.username

    def reset(self):
        self.username = None
        self.password = None


class Idp:
    """
    This class responds to the WAYF form with the selected idp
    """
    def __init__(self, idp=''):
        self.idp = idp or ''

    def set_idps(self, idps):
        """
        set the list of possible idps
        """
        self.raw_idps = idps
        self.idps = idps.keys()
        self.idps.sort()


    def choose_idp(self):
        """
        some how decide what idp to authenticat to
        """
        if self.idp:
            return

        try:
            import struct, fcntl, termios
            def terminal_dimensions():
                fd = os.open(os.ctermid(), os.O_RDONLY)
                if not os.isatty(fd):
                    return (0,0)
                return struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))


            def print_list_wide(items):
                lmax = max([len(x) for x in items]) + 1
                width = terminal_dimensions()[1]
                if width:
                    col = width/lmax
                    i = 1
                    for item in items:
                        if not i%col:
                            print item
                        else:
                            print item.ljust(lmax),
                        i = i + 1
                    if i-1%col:
                        print('')
                else:
                    for item in items:
                        print item
        except:
            def print_list_wide(items):
                for item in items:
                    print item


        idp_list = []
        print self.idps
        for n in range(0, len(self.idps)):
            idp_list.append("%s: %s" % (n + 1, self.idps[n]))
        print_list_wide(idp_list)
        idp_n = 0
        while not idp_n - 1 in range(0, len(self.idps)):
            idp_n = int(raw_input("Idp (1-%i):" % (len(self.idps))))
        self.idp = self.idps[idp_n - 1]


    def get_idp(self):
        """
        return the selected idp
        """
        return self.idp

    def __repr__(self):
        return self.idp

    __str__ = __repr__

    def __eq__(self, value):
        return self.idp.__eq__(value)

    def __hash__(self):
        return self.idp.__hash__()

