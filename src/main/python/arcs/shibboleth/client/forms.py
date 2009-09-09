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


from HTMLParser import HTMLParser
from urllib2 import urlparse
import urllib2, urllib
import logging
from arcs.shibboleth.client.exceptions import WAYFException

log = logging.getLogger('arcs.shibboleth.client')

class FormParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.in_title = False
        self.in_form = False
        self.in_wayf = False
        self.in_ds = False
        self.ds_optgroup = ''
        self.title = ''
        self.forms = []
        self.data = {}

    def handle_starttag(self, tag, attrs):
        self.origin_idp = None
        self.ds_idp = None
        if tag == "title":
            self.in_title = True
        if tag == "form":
            if self.data:
                self.data = {}
            self.in_form = True
            self.data['form'] = dict(attrs)
        if self.in_form and tag == "select" and ('name','origin') in attrs:
            self.in_wayf = True
            self.data['origin'] = {}
        if self.in_form and tag == "select" and ('name',"user_idp") in attrs:
            self.in_ds = True
            self.data['ds'] = {}
        if self.in_form and self.in_ds and tag == "optgroup":
            self.ds_optgroup = dict(attrs)['label']
            self.data['ds'][self.ds_optgroup] = {}
        if self.in_form and self.in_ds and tag == "option":
            origin_idp = dict(attrs)
            if not origin_idp['value'] in ['-', '']:
                self.origin_idp = origin_idp['value']

        if self.in_form and self.in_wayf and tag == "option":
            self.origin_idp = attrs
        if self.in_form and tag == "input":
            attrs = dict(attrs)
            if 'name' in attrs:
                self.data[attrs['name']] = attrs

    def handle_data(self, data):
        if self.in_form and self.in_wayf and self.origin_idp and data.strip():
            self.data['origin'][data.strip()] = self.origin_idp[0][1]
        if self.in_form and self.in_ds and self.origin_idp and data.strip():
            self.data['ds'][self.ds_optgroup][data.strip()] = self.origin_idp
        if self.in_title:
            self.title += data

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "form":
            self.in_form = False
            self.forms.append(self.data)
        if self.in_form and self.in_wayf and tag == "select":
            self.in_wayf = False
        if self.in_form and self.in_ds and tag == "optgroup":
            self.ds_optgroup = ''
        if self.in_form and self.in_ds and tag == "select":
            self.in_ds = False



form_handler_registry = []

class FormHandler(object):
    # The list of form parts to detect
    signature = None
    class __metaclass__(type):
        def __init__(cls, name, bases, dict):
            type.__init__(name, bases, dict)
            if object not in bases:
                form_handler_registry.append((name, cls))


    def __init__(self, title, data, **kwargs):
        self.title = title
        self.data = data

    def submit(self, res):
        raise NotImplementedError

    def prompt(self, printer=None):
        if printer:
            printer(self.title)
        else:
            print(self.title)

class DS(FormHandler):
    form_type = 'ds'
    signature = ['ds', 'Select', 'form', 'session', 'permanent']

    def __init__(self, title, data, **kwargs):
        FormHandler.__init__(self, title, data)
        self.idp = kwargs['idp']

    def submit(self, opener, res):
        """
        submit WAYF form with IDP

        :param idp: the Identity Provider that will be selected at the WAYF
        :param opener: the urllib2 opener
        :param data: the form data as a dictionary
        :param res: the response object
        """
        log.info('Submitting form to wayf')
        headers = {
        "Referer": res.url
        }
        #Set IDP to correct IDP
        wayf_data = {}
        idp = self.idp
        data = self.data
        idps = {}
        for d in data['ds']:
            idps.update(data['ds'][d])
        idp.set_idps(idps)
        idp.choose_idp()
        idp.get_idp()
        if not idps.has_key(idp):
            raise WAYFException("Can't find IdP '%s' in WAYF's IdP list" % idp)
        wayf_data['user_idp'] = idps[idp]
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
    form_type = 'wayf'
    signature = ['origin', 'providerId', 'shire', 'target', 'time']

    def __init__(self, title, data, **kwargs):
        FormHandler.__init__(self, title, data)
        self.idp = kwargs['idp']

    def submit(self, opener, res):
        """
        submit WAYF form with IDP

        :param idp: the Identity Provider that will be selected at the WAYF
        :param opener: the urllib2 opener
        :param data: the form data as a dictionary
        :param res: the response object
        """
        log.info('Submitting form to wayf')
        headers = {
        "Referer": res.url
        }
        #Set IDP to correct IDP
        wayf_data = {}
        idp = self.idp
        data = self.data
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


class IdPFormLogin(FormHandler):
    form_type = 'login'
    signature = ['j_password', 'j_username']
    username_field = signature[1]
    password_field = signature[0]

    def __init__(self, title, data, **kwargs):
        FormHandler.__init__(self, title, data)
        self.cm = kwargs['credentialmanager']

    def submit(self, opener, res):
        """
        submit login form to IdP

        :param opener: the urllib2 opener
        :param data: the form data as a dictionary
        :param res: the response object
        :param cm: a :class:`~slick.passmgr.CredentialManager` containing the URL to the service provider you want to connect to
        """
        if self.cm.tries > 2:
            raise Exception("Too Many Failed Attempts to Authenticate")
        self.cm.tries += 1
        headers = {
        "Referer": res.url
        }
        idp_data = {}
        cm = self.cm
        data = self.data
        url = urlparse.urljoin(res.url, data['form']['action'])
        log.info("Form Authentication from: %s" % url)
        idp_data[self.username_field] = cm.set_username()
        idp_data[self.password_field] = cm.set_password()
        data = urllib.urlencode(idp_data)
        request = urllib2.Request(url, data=data)
        log.info('Submitting login form')
        log.debug("POST: %s" % request.get_full_url())
        response = opener.open(request)
        return request, response


class CASFormLogin(IdPFormLogin):
    form_type = 'cas_login'
    signature = ['password', 'username']
    username_field = signature[1]
    password_field = signature[0]


class IdPSPForm(FormHandler):
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
        headers = {
        "Referer": res.url
        }
        data = self.data
        url = urlparse.urljoin(res.url, data['form']['action'])
        data = urllib.urlencode({'SAMLResponse':data['SAMLResponse']['value'], 'TARGET':'cookie'})
        request = urllib2.Request(url, data=data)
        log.debug("POST: %s" % request.get_full_url())
        response = opener.open(request)
        return request, response


def getFormAdapter(title, forms, idp, cm):
    """
    try to guess what type of form we have encountered

    :param forms: a list of forms, the forms are dictionaries of fields

    return an adapter that can be used to submit the form
    """

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
    return '', None


