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

import sys
import HTMLParser
import BeautifulSoup

is_jython = sys.platform.startswith('java')

if is_jython:
    try:
        from org.apache.log4j import Logger as logging
    except:
        import logging
else:
    import logging

log = logging.getLogger('sibboleth')

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

NESTABLE_TABLE_TAGS = {'table': [],
                       'tr': ['table', 'tbody', 'tfoot', 'thead', 'form'],
                       'td': ['tr'],
                       'th': ['tr'],
                       'thead': ['table'],
                       'tbody': ['table'],
                       'tfoot': ['table'],
                       }

#If one of these tags is encountered, all tags up to the next tag of
#this type are popped.
RESET_NESTING_TAGS = BeautifulSoup.buildTagMap(
    None,
    BeautifulSoup.BeautifulSoup.NESTABLE_BLOCK_TAGS, 'noscript',
    BeautifulSoup.BeautifulSoup.NON_NESTABLE_BLOCK_TAGS,
    BeautifulSoup.BeautifulSoup.NESTABLE_LIST_TAGS,
    NESTABLE_TABLE_TAGS)

NESTABLE_TAGS = BeautifulSoup.buildTagMap(
    [],
    BeautifulSoup.BeautifulSoup.NESTABLE_INLINE_TAGS,
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
