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

import logging
import optparse
from cookielib import MozillaCookieJar
from shibboleth import open_shibprotected_url, list_shibboleth_idps
from credentials import CredentialManager

log = logging.getLogger('shib-cookies')

def main():

    # Populate our options, -h/--help is already there for you.
    usage = "usage: %prog [options] URL"
    optp = optparse.OptionParser(usage=usage)
    optp.add_option("-u", "--username",
                    help="the username to login as.")
    optp.add_option("-p", "--password",
                    help="the password to use.")
    optp.add_option("-o", "--output",
                    help="file to output the cookies to.")
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

    sp = args[0]

    if not opts.idp:
        idps = list_shibboleth_idps(sp)
        idp_keys = idps.keys()
        print "Please specify on of the following IdPs:\n"
        for i in idp_keys:
            print i
        return

    idp = opts.idp
    c = CredentialManager(opts.username, opts.password, log.info)
    cj = MozillaCookieJar()

    if sp:
        log.info("Using IdP: %s" % idp)
        resp = open_shibprotected_url(idp, sp, c, cj)
        for i in resp.readlines():
            print i,

    if opts.output:
        cj.save(opts.output, ignore_discard=True)

