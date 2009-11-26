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
import urllib2
from urllib2 import HTTPCookieProcessor

homedir = os.getenv('USERPROFILE') or os.getenv('HOME')

log = logging.getLogger('shib-logout')

def main(*args):

    # Populate our options, -h/--help is already there for you.
    usage = "usage: %prog [options] URL"
    optp = optparse.OptionParser(usage=usage)
    optp.add_option("-d", "--storedir", dest="store_dir",
                     help="the directory to store the certificate/key and \
                     config file",
                     metavar="DIR",
                     default=path.join(homedir, ".shibboleth"))
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


    if not path.exists(opts.store_dir):
        os.mkdir(opts.store_dir)

    if args:
        sp = args[0]

    # if the cookies file exists load it
    cookies_file = path.join(opts.store_dir, 'cookies.txt')
    cj = MozillaCookieJar(filename=cookies_file)
    if path.exists(cookies_file):
        cj.load()

    logout_urls = []
    for cookie in cj:
        if cookie.name.startswith('_shibsession_') or cookie.name.startswith('_shibstate_'):

            logout_urls.append("https://%s/Shibboleth.sso/Logout" % cookie.domain)


    logout_urls = list(set(logout_urls))

    opener = urllib2.build_opener(HTTPCookieProcessor(cookiejar=cj))
    for url in logout_urls:
        request = urllib2.Request(url)
        log.debug("GET: %s" % request.get_full_url())
        response = opener.open(request)

    cj.save()


if __name__ == "__main__":
    main()

