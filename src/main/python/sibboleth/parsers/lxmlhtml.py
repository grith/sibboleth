#############################################################################
#
# Copyright (c) 2011 Russell Sim <russell.sim@gmail.com> Contributors.
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

from lxml import etree


def lxml_parser(buf):
    """
    Form parser based on LXML etree HTML parser
    """

    html = etree.HTML(''.join(buf.readlines()))

    title = ""
    if html.find('title'):
        title = html.find('title').renderContents()

    forms = []
    for form in html.findall('.//form'):
        formdict = {}
        formdict['form'] = form.attrib

        for s in form.findall('.//select'):
            field = s.attrib

            def to_dict(tag):
                """return a dict from select tag contents"""
                r = {}
                for child in tag.iterchildren():
                    if hasattr(child, 'tag'):
                        if child.tag == 'optgroup':
                            label = child.get('label')
                            r[label] = to_dict(child)
                        if child.tag == 'option':
                            name = child.text
                            url = child.get('value')
                            r.update({name.strip(): url})
                return r

            formdict[s.get('name')] = to_dict(s)

        for i in form.findall('.//input'):
            field = i.attrib
            if field.get('type') == 'submit':
                formdict[i.get('name', 'submit')] = field
            else:
                formdict[field.get('name', 'input')] = field
        forms.append(formdict)

    return html, title, forms
