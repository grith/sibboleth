.. sectionauthor:: Russell Sim <russell@vpac.org>

Introduction
============

This library provides classes to help with using urllib2 to access a shibboleth protected URL.

shib-cookie
-----------

This commandline too was designed to dump cookies from the CookieJar after successfully accessing an SP. These cookies can then be used by other tools like ``wget`` of ``curl`` to access the same shibboleth protected URL.
