import sys

parsers = []

from sibboleth.parsers.htmlparser import html_parser
parsers.append(html_parser)

if not sys.platform.startswith('java'):
    from sibboleth.parsers.lxmlhtml import lxml_parser
    parsers.append(lxml_parser)

from sibboleth.parsers.soup import soup_parser
parsers.append(soup_parser)
