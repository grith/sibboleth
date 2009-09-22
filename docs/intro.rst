.. sectionauthor:: Russell Sim <russell@vpac.org>

Introduction
============

This library provides classes to help with using urllib2 to access a shibboleth protected URL.

shib-login
-----------

This commandline tool was designed to dump cookies from the CookieJar after successfully accessing an SP. These cookies can then be used by other tools like ``wget`` of ``curl`` to access the same shibboleth protected URL.

::

   $ shib-login -i VPAC https://slcs1.arcs.org.au/SLCS/login
   Username [russell]:
   Password:
   Successfully authenticated to https://slcs1.arcs.org.au/SLCS/login
   $ cat ~/.shibboleth/cookies.txt
   # Yummy shibboleth cookies
   slcs1.arcs.org.au       FALSE   /       FALSE   1250598932
   _shibsession_64656561756c7468747470766a2f2f736c6373312e617263732e6f72672e61752f73686962626f6c657468
      _186abd265ea87bf980fae2a16b0243e2


   $ curl -b ~/.shibboleth/cookies.txt https://slcs1.arcs.org.au/SLCS/login
   <?xml version="1.0" encoding="UTF-8" ?>
   <SLCSLoginResponse>
   ......

   $ wget --load-cookies ~/.shibboleth/cookies.txt https://slcs1.arcs.org.au/SLCS/login
   --2009-08-18 14:35:53--  https://slcs1.arcs.org.au/SLCS/login
   Resolving slcs1.arcs.org.au... 202.158.218.211
   Connecting to slcs1.arcs.org.au|202.158.218.211|:443... connected.
   HTTP request sent, awaiting response... 200 OK
   .......

