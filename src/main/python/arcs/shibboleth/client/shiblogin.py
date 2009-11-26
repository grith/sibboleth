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
from os import path
import logging
import optparse
from cookielib import MozillaCookieJar
from shibboleth import Shibboleth
from credentials import CredentialManager, Idp

homedir = os.getenv('USERPROFILE') or os.getenv('HOME')

log = logging.getLogger('shib-login')

def main(*args):

    # Populate our options, -h/--help is already there for you.
    usage = "usage: %prog [options] URL"
    optp = optparse.OptionParser(usage=usage)
    optp.add_option("-u", "--username",
                    help="the username to login as.")
    optp.add_option("-d", "--storedir", dest="store_dir",
                     help="the directory to store the certificate/key and \
                     config file",
                     metavar="DIR",
                     default=path.join(homedir, ".shibboleth"))
    optp.add_option("-i", "--idp",
                    help="unique ID of the IdP used to log in")
    optp.add_option('-v', '--verbose', dest='verbose', action='count',
                    help="Increase verbosity (specify multiple times for more)")
    # Parse the arguments (defaults to parsing sys.argv).
    opts, args = optp.parse_args()

    # Here would be a good place to check what came in on the command line and
    # call optp.error("Useful message") to exit if all it not well.

    log_level = logging.WARNING # default
    if opts.verbose == 1:
        log_level = logging.INFO
    elif opts.verbose >= 2:
        log_level = logging.DEBUG

    # Set up basic configuration, out to stderr with a reasonable default format.
    logging.basicConfig(level=log_level)

    if not args:
        optp.print_help()
        return

    if not path.exists(opts.store_dir):
        os.mkdir(opts.store_dir)

    sp = args[0]


    idp = Idp(opts.idp)
    c = CredentialManager()
    if opts.username:
        c.username = opts.username

    # if the cookies file exists load it
    cookies_file = path.join(opts.store_dir, 'cookies.txt')
    cj = MozillaCookieJar(filename=cookies_file)
    if path.exists(cookies_file):
        cj.load()

    shibboleth = Shibboleth(idp, c, cj)
    shibboleth.openurl(sp)
    print("Successfully authenticated to %s" % sp)

    cj.save()


if __name__ == "__main__":
    main()

