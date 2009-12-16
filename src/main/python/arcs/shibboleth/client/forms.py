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


from BeautifulSoup import BeautifulSoup
from urllib2 import urlparse
import urllib2, urllib
import logging
from arcs.shibboleth.client.exceptions import WAYFException

log = logging.getLogger('arcs.shibboleth.client')


class Result(object):
    def __init__(self):
        self.ds_optgroup = ''
        self.title = ''
        self.forms = []


def soup_parser(buf):
    soup = BeautifulSoup(buf)
    r = Result()

    if soup.find('title'):
        r.title = soup.find('title').renderContents()

    forms = soup.findAll('form')
    formlist = []
    for form in forms:
        formdict = {}
        formdict['form'] = dict(form.attrs)

        for s in form.findAll('select'):
            field = dict(s.attrs)
            def to_dict(tag):
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
            if field['type'] == 'submit':
                formdict[i.get('name', 'submit')] = field
            else:
                formdict[field.get('name', 'input')] = field
        formlist.append(formdict)
        r.forms = formlist
    return r


form_handler_registry = []

class FormHandler(object):
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

    def submit(self, res):
        raise NotImplementedError


class DS(FormHandler):
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
        headers = {
        "Referer": res.url
        }
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
        headers = {
        "Referer": res.url
        }
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
        headers = {
        "Referer": res.url
        }
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
        headers = {
        "Referer": res.url
        }
        data = self.data
        url = urlparse.urljoin(res.url, data['form']['action'])
        data = urllib.urlencode({'SAMLResponse':data['SAMLResponse']['value'], 'RelayState':'cookie'})
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


