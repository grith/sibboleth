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

import HTMLParser
import pprint
import unittest


class EventCollector(HTMLParser.HTMLParser):

    def __init__(self):
        self.events = []
        self.append = self.events.append
        HTMLParser.HTMLParser.__init__(self)

    def get_events(self):
        # Normalize the list of events so that buffer artefacts don't
        # separate runs of contiguous characters.
        L = []
        prevtype = None
        for event in self.events:
            type = event[0]
            if type == prevtype == "data":
                L[-1] = ("data", L[-1][1] + event[1])
            else:
                L.append(event)
            prevtype = type
        self.events = L
        return L

    # structure markup

    def handle_starttag(self, tag, attrs):
        self.append(("starttag", tag, attrs))

    def handle_startendtag(self, tag, attrs):
        self.append(("startendtag", tag, attrs))

    def handle_endtag(self, tag):
        self.append(("endtag", tag))

    # all other markup

    def handle_comment(self, data):
        self.append(("comment", data))

    def handle_charref(self, data):
        self.append(("charref", data))

    def handle_data(self, data):
        self.append(("data", data))

    def handle_decl(self, data):
        self.append(("decl", data))

    def handle_entityref(self, data):
        self.append(("entityref", data))

    def handle_pi(self, data):
        self.append(("pi", data))

    def unknown_decl(self, decl):
        self.append(("unknown decl", decl))


class EventCollectorExtra(EventCollector):

    def handle_starttag(self, tag, attrs):
        EventCollector.handle_starttag(self, tag, attrs)
        self.append(("starttag_text", self.get_starttag_text()))


class TestCaseBase(unittest.TestCase):

    def _run_check(self, source, expected_events, collector=EventCollector):
        parser = collector()
        for s in source:
            parser.feed(s)
        parser.close()
        events = parser.get_events()
        if events != expected_events:
            self.fail("received events did not match expected events\n"
                      "Expected:\n" + pprint.pformat(expected_events) +
                      "\nReceived:\n" + pprint.pformat(events))

    def _run_check_extra(self, source, events):
        self._run_check(source, events, EventCollectorExtra)

    def _parse_error(self, source):
        def parse(source=source):
            parser = HTMLParser.HTMLParser()
            parser.feed(source)
            parser.close()
        self.assertRaises(HTMLParser.HTMLParseError, parse)


class TestParserModifications(TestCaseBase):

    def test_attr_syntax(self):
        output = [("starttag", "a", [("b", "v"), ("c", "v"),
                                     ("d", "v"), ("e", None)])]
        self._run_check("""<a b='v'c="v" d=v e>""", output)
        # TODO make the unittest below pass
        #self._run_check("""<a b="v" c=v d=v">""", output)

    def test_startendtag(self):
        # test end tag with attributes
        self._run_check("<p></p d='t'>", [
            ("starttag", "p", []),
            ("endtag", "p"),
            ])
