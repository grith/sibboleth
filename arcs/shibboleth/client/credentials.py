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

class CredentialManager:
    """
    This class is responsible for displaying information about the location
    being authed too, and receiving user name and password from the user.
    """

    def __init__(self, username=None, password=None, printfunc=None):
        self.username = username
        self.password = password
        self.printfunc = printfunc

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

    def print_realm(self, realm):
        if self.printfunc:
            self.printfunc(realm)
            return
        print(realm)

    def reset(self):
        self.username = None
        self.password = None

