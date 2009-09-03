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

import urllib2, urllib
from HTMLParser import HTMLParser
from urllib2 import HTTPCookieProcessor, HTTPRedirectHandler, urlparse
from urllib2 import HTTPBasicAuthHandler
from time import time
import logging
import re

from arcs.shibboleth.client.exceptions import WAYFException


log = logging.getLogger('arcs.shibboleth.client')




class ShibbolethHandler(HTTPRedirectHandler, HTTPCookieProcessor):

    def __init__(self, cookiejar=None, **kwargs):
        HTTPCookieProcessor.__init__(self, cookiejar ,**kwargs)

    def http_error_302(self, req, fp, code, msg, headers):
        log.debug("GET %s" % req.get_full_url())
        result = HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
        result.status = code
        return result

    http_error_301 = http_error_303 = http_error_307 = http_error_302


class ShibbolethAuthHandler(HTTPBasicAuthHandler, ShibbolethHandler):

    def __init__(self, credentialmanager=None, cookiejar=None, **kwargs):
        HTTPBasicAuthHandler.__init__(self)
        ShibbolethHandler.__init__(self, cookiejar=cookiejar)
        self.credentialmanager = credentialmanager

    def http_error_401(self, req, fp, code, msg, headers):
        """Basic Auth handler"""
        url = req.get_full_url()
        authline = headers.getheader('www-authenticate')
        authobj = re.compile(
            r'''(?:\s*www-authenticate\s*:)?\s*(\w*)\s+realm=['"]([^'"]+)['"]''',
            re.IGNORECASE)
        matchobj = authobj.match(authline)
        realm = matchobj.group(2)
        self.credentialmanager.print_realm(realm)
        user = self.credentialmanager.get_username()
        self.credentialmanager.get_password()
        passwd = self.credentialmanager.get_password()
        self.add_password(realm=realm, uri=url, user=user, passwd=passwd)
        return self.http_error_auth_reqed('www-authenticate',
                                          url, req, headers)


class FormParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.in_title = False
        self.in_form = False
        self.in_origin = False
        self.title = ''
        self.forms = []
        self.data = {}

    def handle_starttag(self, tag, attrs):
        self.origin_idp = None
        if tag == "title":
            self.in_title = True
        if tag == "form":
            if self.data:
                self.data = {}
            self.in_form = True
            self.data['form'] = dict(attrs)
        if self.in_form and tag == "select" and ('name','origin') in attrs:
            self.in_origin = True
            self.data['origin'] = {}
        if self.in_form and self.in_origin and tag == "option":
            self.origin_idp = attrs
        if self.in_form and tag == "input":
            attrs = dict(attrs)
            if 'name' in attrs:
                self.data[attrs['name']] = attrs
    def handle_data(self, data):
        if self.in_form and self.in_origin and self.origin_idp and data.strip():
            self.data['origin'][data.strip()] = self.origin_idp[0][1]
        if self.in_title:
            self.title += data

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "form":
            self.in_form = False
            self.forms.append(self.data)
        if self.in_form and self.in_origin and tag == "select":
            self.in_origin = False


def submitWayfForm(idp, opener, data, res):
    """
    submit WAYF form with IDP

    :param idp: the Identity Provider that will be selected at the WAYF
    :param opener: the urllib2 opener
    :param data: the form data as a dictionary
    :param res: the response object
    """
    headers = {
    "Referer": res.url
    }
    #Set IDP to correct IDP
    wayf_data = {}
    idp.set_idps(data['origin'])
    idp.choose_idp()
    idp.get_idp()
    if not data['origin'].has_key(idp):
        raise WAYFException("Can't find IdP '%s' in WAYF's IdP list" % idp)
    wayf_data['origin'] = data['origin'][idp]
    wayf_data['shire'] = data['shire']['value']
    wayf_data['providerId'] = data['providerId']['value']
    wayf_data['target'] = data['target']['value']
    wayf_data['time'] = data['time']['value']
    wayf_data['cache'] = 'false'
    wayf_data['action'] = 'selection'
    url = urlparse.urljoin(res.url, data['form']['action'])
    data = urllib.urlencode(wayf_data)
    request = urllib2.Request(url + '?' + data)
    log.debug("POST: %s" % request.get_full_url())
    response = opener.open(request)
    return request, response


def submitIdpForm(opener, title, data, res, cm):
    """
    submit login form to IdP

    :param opener: the urllib2 opener
    :param title: the title of the IdP login page
    :param data: the form data as a dictionary
    :param res: the response object
    :param cm: a :class:`~slick.passmgr.CredentialManager` containing the URL to the service provider you want to connect to
    """
    headers = {
    "Referer": res.url
    }
    idp_data = {}
    url = urlparse.urljoin(res.url, data['form']['action'])
    log.info("Form Authentication from: %s" % url)
    cm.print_realm(title)
    idp_data['j_username'] = cm.get_username()
    cm.get_password()
    idp_data['j_password'] = cm.get_password()
    data = urllib.urlencode(idp_data)
    request = urllib2.Request(url, data=data)
    log.info('Submitting login form')
    log.debug("POST: %s" % request.get_full_url())
    response = opener.open(request)
    return request, response


def submitFormToSP(opener, data, res):
    """
    submit IdP form to SP

    :param opener: the urllib2 opener
    :param data: the form data as a dictionary
    :param res: the response object
    """
    headers = {
    "Referer": res.url
    }
    url = urlparse.urljoin(res.url, data['form']['action'])
    data = urllib.urlencode({'SAMLResponse':data['SAMLResponse']['value'], 'TARGET':'cookie'})
    request = urllib2.Request(url, data=data)
    log.debug("POST: %s" % request.get_full_url())
    response = opener.open(request)
    return request, response


def whatForm(forms):
    """
    try to guess what type of form we have encountered

    :param forms: a list of forms, the forms are dictionaries of fields
    """
    form_types = {'wayf': ['origin', 'providerId', 'shire', 'target', 'time'],
                  'login': ['j_password', 'j_username'],
                  'idp': ['SAMLResponse', 'TARGET'],
    }

    def match_form(form, type, items):
        for i in items:
            if i not in form.keys():
                rtype = None
                rform = None
                break
            rtype = type
            rform = form
        return rtype, rform

    for form in forms:
        for ft in form_types:
            rtype,rform = match_form(form, ft, form_types[ft])
            if rtype:
                return rtype,rform
    return '', None


def list_shibboleth_idps(sp):
    """
    return a list of idps protecting a service provider.

    :param sp: the URL of the service provider you want to connect to

    """
    opener = urllib2.build_opener(ShibbolethAuthHandler())
    request = urllib2.Request(sp)
    log.debug("GET: %s" % request.get_full_url())
    response = opener.open(request)
    parser = FormParser()
    for line in response:
        parser.feed(line)
    type, form = whatForm(parser.forms)
    if type == 'wayf':
        return form['origin']
    raise("Unknown error: Shibboleth auth chain lead to nowhere")


def open_shibprotected_url(idp, sp, cm, cj):
    """
    return a urllib response from the service once shibboleth authentication is complete.

    :param idp: the Identity Provider that will be selected at the WAYF
    :param sp: the URL of the service provider you want to connect to
    :param cm: a :class:`~slick.passmgr.CredentialManager` containing the URL to the service provider you want to connect to
    :param cj: the cookie jar that will be used to store the shibboleth cookies
    """
    cookiejar = cj
    opener = urllib2.build_opener(ShibbolethAuthHandler(credentialmanager=cm, cookiejar=cookiejar))
    request = urllib2.Request(sp)
    log.debug("GET: %s" % request.get_full_url())
    response = opener.open(request)

    slcsresp = None
    tries = 0
    while(not slcsresp):
        parser = FormParser()
        for line in response:
            parser.feed(line)
        parser.close()
        type, form = whatForm(parser.forms)
        if type == 'wayf':
            log.info('Submitting form to wayf')
            request, response = submitWayfForm(idp, opener, form, response)
            continue
        if type == 'login':
            if tries > 2:
                raise Exception("Too Many Failed Attempts to Authenticate")
            request, response = submitIdpForm(opener, parser.title, form, response, cm)
            tries += 1
            continue
        if type == 'idp':
            log.info('Submitting IdP SAML form')
            request, response = submitFormToSP(opener, form, response)
            set_cookies_expiries(cj)
            return response
        raise("Unknown error: Shibboleth auth chain lead to nowhere")


def set_cookies_expiries(cookiejar):
    """
    Set the shibboleth session cookies to the default SP expiry, this way
    the cookies can be used by other applications.
    The cookes that are modified are ``_shibsession_`` and ``_shibstate_``

    :param cj: the cookie jar that stores the shibboleth cookies
    """
    for cookie in cookiejar:
        if cookie.name.startswith('_shibsession_'):
            if not cookie.expires:
                cookie.expires = int(time()) + 28800
                cookie.discard = False

from arcs.shibboleth.client.credentials import CredentialManager, Idp
from cookielib import CookieJar

try:
    from au.org.arcs.auth.shibboleth import ShibbolethClient as shib_interface
except:
    shib_interface = object


class Shibboleth(shib_interface):
    def __init__(self):
        self.cj = CookieJar()

    def shibopen(self, url, username, password, idp):

        def antiprint(*args):
            pass

        idp = Idp(idp)
        c = CredentialManager(username, password, antiprint)
        r = open_shibprotected_url(self.idp, url, self.c, self.cj)
        del c, idp
        return r

    def open(self, url):
        opener = urllib2.build_opener(ShibbolethHandler(cookiejar=self.cj))
        request = urllib2.Request(url)
        return opener.open(request)

