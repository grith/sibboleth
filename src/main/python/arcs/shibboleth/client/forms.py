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


import HTMLParser
import BeautifulSoup
from urllib2 import urlparse
import urllib2, urllib
import logging
from arcs.shibboleth.client.exceptions import WAYFException

log = logging.getLogger('arcs.shibboleth.client')

import re
endtagfind = re.compile("""
  </\s*([a-zA-Z][-.a-zA-Z0-9:_]*)
  (?:\s+                             # whitespace before attribute name
    (?:[a-zA-Z_][-.:a-zA-Z0-9_]*     # attribute name
      (?:\s*=\s*                     # value indicator
        (?:'[^']*'                   # LITA-enclosed value
          |\"[^\"]*\"                # LIT-enclosed value
          |[^'\">\s]+                # bare value
         )
       )?
     )*
   )*
\s*>
""", re.VERBOSE)
HTMLParser.endtagfind = endtagfind

locatestarttagend = re.compile(r"""
  <[a-zA-Z][-.a-zA-Z0-9:_]*          # tag name
  (?:\s+                             # whitespace before attribute name
    (?:[a-zA-Z_][-.:a-zA-Z0-9_]*     # attribute name
      (?:\s*=\s*                     # value indicator
        (?:'[^']*'                   # LITA-enclosed value
          |\"[^\"]*\"                # LIT-enclosed value
          |\\"[^\"]*\\"              # Escaped " , i.e. \"
          |[^'\">\s]+                # bare value
         )
       )?
     )*
   )*
  \s*                                # trailing whitespace
""", re.VERBOSE)
HTMLParser.locatestarttagend = locatestarttagend

attrfind = re.compile(
    r'\s*([a-zA-Z_][-.:a-zA-Z_0-9]*)(\s*=\s*'
    r'(\'[^\']*\'|"[^"]*"|\\"[^"]*\\"|[-a-zA-Z0-9./,:;+*%?!&$\(\)_#=~@]*))?')
HTMLParser.attrfind = attrfind

NESTABLE_TABLE_TAGS = {'table' : [],
                       'tr' : ['table', 'tbody', 'tfoot', 'thead', 'form'],
                       'td' : ['tr'],
                       'th' : ['tr'],
                       'thead' : ['table'],
                       'tbody' : ['table'],
                       'tfoot' : ['table'],
                       }

#If one of these tags is encountered, all tags up to the next tag of
#this type are popped.
RESET_NESTING_TAGS = BeautifulSoup.buildTagMap(None, BeautifulSoup.BeautifulSoup.NESTABLE_BLOCK_TAGS, 'noscript',
                                 BeautifulSoup.BeautifulSoup.NON_NESTABLE_BLOCK_TAGS,
                                 BeautifulSoup.BeautifulSoup.NESTABLE_LIST_TAGS,
                                 NESTABLE_TABLE_TAGS)

NESTABLE_TAGS = BeautifulSoup.buildTagMap([], BeautifulSoup.BeautifulSoup.NESTABLE_INLINE_TAGS,
                                BeautifulSoup.BeautifulSoup.NESTABLE_BLOCK_TAGS,
                                BeautifulSoup.BeautifulSoup.NESTABLE_LIST_TAGS,
                                NESTABLE_TABLE_TAGS)

BeautifulSoup.BeautifulSoup.NESTABLE_TABLE_TAGS = NESTABLE_TABLE_TAGS
BeautifulSoup.BeautifulSoup.NESTABLE_TAGS = NESTABLE_TAGS
BeautifulSoup.BeautifulSoup.RESET_NESTING_TAGS = RESET_NESTING_TAGS


def soup_parser(buf):
    """
    Form parser based on Beautiful Soup
    """
    soup = BeautifulSoup.BeautifulSoup(buf)

    title = ""
    if soup.find('title'):
        title = soup.find('title').renderContents()

    forms = []
    for form in soup.findAll('form'):
        formdict = {}
        formdict['form'] = dict(form.attrs)

        for s in form.findAll('select'):
            field = dict(s.attrs)
            def to_dict(tag):
                """return a dict from select tag contents"""
                r = {}
                for child in tag.childGenerator():
                    if hasattr(child, 'name'):
                        if child.name == 'optgroup':
                            label = child.get('label')
                            r[label] = to_dict(child)
                        if child.name == 'option':
                            name = child.renderContents()
                            url = child.get('value')
                            r.update({name.strip(): url})
                return r

            formdict[s.get('name')] = to_dict(s)

        for i in form.findAll('input'):
            field = dict(i.attrs)
            if field.get('type') == 'submit':
                formdict[i.get('name', 'submit')] = field
            else:
                formdict[field.get('name', 'input')] = field
        forms.append(formdict)
    return soup, title, forms


form_handler_registry = []

class FormHandler(object):
    """
    Base Form Handler Class
    """
    # The list of form parts to detect
    signature = None
    interactive = False

    class __metaclass__(type):
        def __init__(cls, name, bases, dict):
            type.__init__(cls, name, bases, dict)
            if object not in bases:
                form_handler_registry.append((name, cls))

    def __init__(self, title, data, **kwargs):
        self.title = title
        self.data = data

    def submit(self, opener, res):
        raise NotImplementedError


class DS(FormHandler):
    """
    Discovery Service Handler
    """
    form_type = 'ds'
    signature = ['user_idp', 'Select', 'form', 'session', 'permanent']
    interactive = True

    def __init__(self, title, data, **kwargs):
        FormHandler.__init__(self, title, data)
        self.idp = kwargs['idp']

    def prompt(self, shibboleth):
        idps = {}
        for d in self.data['user_idp']:
            if isinstance(self.data['user_idp'][d], dict):
                idps.update(self.data['user_idp'][d])
        self.idp.set_idps(idps)
        return self.idp.prompt(shibboleth)

    def submit(self, opener, res):
        """
        submit WAYF form with IDP

        :param opener: the urllib2 opener
        :param data: the form data as a dictionary
        :param res: the response object
        """
        log.info('Submitting form to wayf')
        #Set IDP to correct IDP
        wayf_data = {}
        idp = self.idp
        data = self.data
        idps = {}
        for d in data['user_idp']:
            if isinstance(data['user_idp'][d], dict):
                idps.update(data['user_idp'][d])
        if not idps.has_key(idp.get_idp()):
            raise WAYFException("Can't find IdP '%s' in WAYF's IdP list" % idp)
        wayf_data['user_idp'] = idps[idp.get_idp()]
        wayf_data['Select'] = 'Select'
        if data['form']['action'].startswith('?'):
            urlsp = urlparse.urlsplit(res.url)
            urlsp = urlparse.urlunsplit((urlsp[0], urlsp[1], urlsp[2], '', ''))
            url = res.url + data['form']['action']
        else:
            url = urlparse.urljoin(res.url, data['form']['action'])
        data = urllib.urlencode(wayf_data)
        request = urllib2.Request(url, data)
        log.debug("POST: %s" % request.get_full_url())
        response = opener.open(request)
        return request, response


class WAYF(FormHandler):
    """
    Where Are You From Handler
    """
    form_type = 'wayf'
    signature = ['origin', 'providerId', 'shire', 'target', 'time']
    interactive = True

    def __init__(self, title, data, **kwargs):
        FormHandler.__init__(self, title, data)
        self.idp = kwargs['idp']

    def prompt(self, shibboleth):
        self.idp.set_idps(self.data['origin'])
        return self.idp.prompt(shibboleth)

    def submit(self, opener, res):
        """
        submit WAYF form with IDP

        :param opener: the urllib2 opener
        :param data: the form data as a dictionary
        :param res: the response object
        """
        log.info('Submitting form to wayf')
        #Set IDP to correct IDP
        wayf_data = {}
        idp = self.idp
        data = self.data
        if not data['origin'].has_key(idp.get_idp()):
            raise WAYFException("Can't find IdP '%s' in WAYF's IdP list" % idp.get_idp())
        wayf_data['origin'] = data['origin'][idp.get_idp()]
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


class IdPFormLogin(FormHandler):
    """
    IDP Form Login Handler
    """
    form_type = 'login'
    signature = ['j_password', 'j_username']
    username_field = signature[1]
    password_field = signature[0]
    interactive = True

    def __init__(self, title, data, **kwargs):
        FormHandler.__init__(self, title, data)
        self.cm = kwargs['credentialmanager']

    def prompt(self, shibboleth):
        self.cm.set_title(self.title)
        return self.cm.prompt(shibboleth)

    def submit(self, opener, res):
        """
        submit login form to IdP

        :param opener: the urllib2 opener
        :param data: the form data as a dictionary
        :param res: the response object
        :param cm: a :class:`~slick.passmgr.CredentialManager` containing the URL to the service provider you want to connect to
        """
        idp_data = {}
        cm = self.cm
        data = self.data
        url = urlparse.urljoin(res.url, data['form']['action'])
        log.info("Form Authentication from: %s" % url)
        idp_data[self.username_field] = cm.get_username()
        idp_data[self.password_field] = cm.get_password()
        data = urllib.urlencode(idp_data)
        request = urllib2.Request(url, data=data)
        log.info('Submitting login form')
        log.debug("POST: %s" % request.get_full_url())
        response = opener.open(request)
        return request, response


class CASFormLogin(IdPFormLogin):
    """
    CAS Form Login Handler
    """
    form_type = 'cas_login'
    signature = ['password', 'username']
    username_field = signature[1]
    password_field = signature[0]


class ESOEFormLogin(IdPFormLogin):
    """
    ESOE Form Login Handler
    """
    form_type = 'esoe_login'
    signature = ['esoeauthn_pw', 'esoeauthn_user']
    username_field = signature[1]
    password_field = signature[0]


class COSignFormLogin(IdPFormLogin):
    """
    COSign Form Login Handler
    """
    form_type = 'cosign_login'
    signature = ['password', 'login']
    username_field = signature[1]
    password_field = signature[0]

    def submit(self, opener, res):
        """
        submit login form to COSign IdP

        :param opener: the urllib2 opener
        :param data: the form data as a dictionary
        :param res: the response object
        :param cm: a :class:`~slick.passmgr.CredentialManager` containing the URL to the service provider you want to connect to
        """
        idp_data = {}
        cm = self.cm
        data = self.data
        url = urlparse.urljoin(res.url, data['form']['action'])
        log.info("Form Authentication from: %s" % url)
        idp_data[self.username_field] = cm.get_username()
        idp_data[self.password_field] = cm.get_password()
        idp_data['service'] = data['service']['value']
        idp_data['ref'] = data['ref']['value']
        data = urllib.urlencode(idp_data)
        request = urllib2.Request(url, data=data)
        log.info('Submitting login form')
        log.debug("POST: %s" % request.get_full_url())
        response = opener.open(request)
        return request, response


class IdPSPForm(FormHandler):
    """
    IDP Post-back Form Handler
    """
    form_type = 'idp'
    signature = ['SAMLResponse', 'TARGET']


    def submit(self, opener, res):
        """
        submit IdP form to SP

        :param opener: the urllib2 opener
        :param data: the form data as a dictionary
        :param res: the response object
        """
        log.info('Submitting IdP SAML form')
        data = self.data
        url = urlparse.urljoin(res.url, data['form']['action'])
        data = urllib.urlencode({'SAMLResponse':data['SAMLResponse']['value'], 'TARGET':'cookie'})
        request = urllib2.Request(url, data=data)
        log.debug("POST: %s" % request.get_full_url())
        response = opener.open(request)
        return request, response


class IdPSPFormRelayState(FormHandler):
    """
    Slight variation on the IdPSPForm
    """
    form_type = 'idp'
    signature = ['SAMLResponse', 'RelayState']


    def submit(self, opener, res):
        """
        submit IdP form to SP

        :param opener: the urllib2 opener
        :param data: the form data as a dictionary
        :param res: the response object
        """
        log.info('Submitting IdP SAML form')
        data = self.data
        url = urlparse.urljoin(res.url, data['form']['action'])
        data = urllib.urlencode({'SAMLResponse':data['SAMLResponse']['value'], 'RelayState':'cookie'})
        request = urllib2.Request(url, data=data)
        log.debug("POST: %s" % request.get_full_url())
        response = opener.open(request)
        return request, response


class SAMLRequest(FormHandler):
    """
    Slight variation on the IdPSPForm
    """
    form_type = 'samlrequest'
    signature = ['SAMLRequest']


    def submit(self, opener, res):
        """
        submit IdP form to SP

        :param opener: the urllib2 opener
        :param data: the form data as a dictionary
        :param res: the response object
        """
        log.info('Submitting SAML Verification form')
        data = self.data
        url = urlparse.urljoin(res.url, data['form']['action'])
        data = urllib.urlencode({'SAMLRequest':data['SAMLRequest']['value']})
        request = urllib2.Request(url, data=data)
        log.debug("POST: %s" % request.get_full_url())
        response = opener.open(request)
        return request, response


page_handler_registry = []

class PageHandler(object):
    # The list of form parts to detect
    signature = None
    interactive = False

    class __metaclass__(type):
        def __init__(cls, name, bases, dict):
            type.__init__(cls, name, bases, dict)
            if object not in bases:
                page_handler_registry.append((name, cls))

    def __init__(self, page, **kwargs):
        self.page = page

    def submit(self, opener, res):
        raise NotImplementedError


class ESOEChooser(PageHandler):
    """
    Slight variation on the IdPSPForm
    """
    type = 'esoe'

    def __init__(self, *args, **kwargs):
        PageHandler.__init__(self, *args, **kwargs)
        self.url = ''

    def can_adapt(self):
        links = self.page.findAll('a')

        for l in links:
            if l.get('href') == 'enterpriselogin.htm':
                self.url = l.get('href')
                return True
        return False


    def submit(self, opener, res):
        """
        follow login link on ESOE Chooser page

        :param opener: the urllib2 opener
        :param data: the form data as a dictionary
        :param res: the response object
        """
        url = urlparse.urljoin(res.url, self.url)
        request = urllib2.Request(url)
        log.debug("GET: %s" % request.get_full_url())
        response = opener.open(request)
        return request, response


def getFormAdapter(response, idp, cm):
    """
    try to guess what type of form we have encountered

    :param forms: a list of forms, the forms are dictionaries of fields

    return an adapter that can be used to submit the form
    """

    parser, title, forms = soup_parser(response)

    def match_form(form, items):
        for i in items:
            if i not in form.keys():
                rform = None
                break
            rform = form
        return rform

    for form in forms:
        for name, adapter in form_handler_registry:
            radapter = match_form(form, adapter.signature)
            if radapter:
                return adapter.form_type, adapter(title, form, idp=idp, credentialmanager=cm)

    for name, adapter in page_handler_registry:
        radapter = adapter(parser, idp=idp, credentialmanager=cm)
        if radapter.can_adapt():
            return radapter.type, radapter

    return '', None


