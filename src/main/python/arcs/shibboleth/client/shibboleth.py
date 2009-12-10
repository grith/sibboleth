##############################################################################
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
##############################################################################

from urlparse import urlsplit, urljoin
import urllib2
from urllib2 import HTTPCookieProcessor, HTTPRedirectHandler
from urllib2 import HTTPBasicAuthHandler
from time import time
import logging
import re
from arcs.shibboleth.client.forms import FormParser, getFormAdapter
import sys

is_jython = sys.platform.startswith('java')

log = logging.getLogger('arcs.shibboleth.client')


class ShibbolethHandler(HTTPRedirectHandler, HTTPCookieProcessor):

    def __init__(self, cookiejar=None, **kwargs):
        HTTPCookieProcessor.__init__(self, cookiejar, **kwargs)

    def http_error_302(self, req, fp, code, msg, headers):
        if 'location' in headers:
            newurl = headers.getheaders('location')[0]
        elif 'uri' in headers:
            newurl = headers.getheaders('uri')[0]
        newurl = urljoin(req.get_full_url(), newurl)
        log.debug("302 %s" % newurl)

        result = HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)

        return result

    http_error_301 = http_error_303 = http_error_307 = http_error_302


class ShibbolethAuthHandler(HTTPBasicAuthHandler, ShibbolethHandler):

    def __init__(self, credentialmanager=None, cookiejar=None, **kwargs):
        HTTPBasicAuthHandler.__init__(self)
        ShibbolethHandler.__init__(self, cookiejar=cookiejar)
        self.credentialmanager = credentialmanager
        self.__req = None
        self.__headers = None

    def http_error_401(self, req, fp, code, msg, headers):
        """Basic Auth handler"""
        self.__req = req
        self.__headers = headers
        authline = headers.getheader('www-authenticate')
        authobj = re.compile(
            r'''(?:\s*www-authenticate\s*:)?\s*(\w*)\s+realm=['"]([^'"]+)['"]''',
            re.IGNORECASE)
        matchobj = authobj.match(authline)
        self.realm = matchobj.group(2)
        self.credentialmanager.set_title(self.realm)
        return self.credentialmanager.prompt(self)

    def run(self):
        url = self.__req.get_full_url()
        self.add_password(realm=self.realm, uri=url,
                          user=self.credentialmanager.get_username(),
                          passwd=self.credentialmanager.get_password())
        return self.http_error_auth_reqed('www-authenticate',
                                          url, self.__req, self.__headers)


def set_cookies_expiries(cookiejar):
    """
    Set the shibboleth session cookies to the default SP expiry, this way
    the cookies can be used by other applications.
    The cookes that are modified are ``_shibsession_``

    :param cj: the cookie jar that stores the shibboleth cookies
    """
    for cookie in cookiejar:
        if cookie.name.startswith('_shibsession_'):
            if not cookie.expires:
                cookie.expires = int(time()) + 28800
                cookie.discard = False

from cookielib import CookieJar

if is_jython:
    from au.org.arcs.auth.shibboleth import ShibbolethClient as shib_interface
else:
    shib_interface = object


class Shibboleth(shib_interface):
    """
    return a urllib response from the service once shibboleth authentication is complete.

    :param idp: the Identity Provider that will be selected at the WAYF
    :param cm: a :class:`~arcs.shibboleth.client.credentials.CredentialManager` containing the URL to the service provider you want to connect to
    :param cj: the cookie jar that will be used to store the shibboleth cookies
    """
    def __init__(self, idp, cm, cookiejar=None, proxies=None):
        if not cookiejar == None:
            self.cookiejar = cookiejar
        else:
            self.cookiejar = CookieJar()
        self.idp = idp
        self.cm = cm

        shib_auth_handler = ShibbolethAuthHandler(credentialmanager=self.cm, cookiejar=self.cookiejar)
        proxy_support = urllib2.ProxyHandler(proxies=proxies)
        self.opener = urllib2.build_opener(proxy_support, shib_auth_handler)

        self.__listeners = []

    def add_listener(self, listener):
        """
        add a listner that will be called when the shibboleth authentication process is finished.

        the method signature of the listner can optionally take one argument which will be the response.
        """
        self.__listeners.append(listener)

    def openurl(self, url=None):
        """
        return the response object as a result of opens the url

        :param url: the URL of the service provider you want to connect to
        """
        if url:
            self.url = url
        log.debug("GET %s" % self.url)
        request = urllib2.Request(self.url)
        self.response = self.opener.open(request)
        return self.__follow_chain(self.response)

    def __follow_chain(self, response):
        for c in self.cookiejar:
            if c.name.startswith('_shibsession_') and c.domain == urlsplit(self.url)[1]:
                set_cookies_expiries(self.cookiejar)
                self.response = response
                for l in self.__listeners:
                    try:
                        l(response)
                    except TypeError:
                        l()
                return response

        parser = FormParser()
        for line in response:
            parser.feed(line)
        parser.close()
        type, adapter = getFormAdapter(parser.title, parser.forms, self.idp, self.cm)

        if adapter:
            if adapter.interactive:
                self.adapter = adapter
                self.response = response
                response = adapter.prompt(self)
                if response:
                    return response
                return
            else:
                request, response = adapter.submit(self.opener, response)
                return self.__follow_chain(response)

        raise("Unknown error: Shibboleth auth chain lead to nowhere")

    def run(self):
        """
        used by the :class:`~arcs.shibboleth.client.credentials.Idp` and :class:`~arcs.shibboleth.client.credentials.CredentialManager` controllers to resume the shibboleth auth.
        """
        request, response = self.adapter.submit(self.opener, self.response)
        return self.__follow_chain(response)

    def get_response(self):
        return self.response
