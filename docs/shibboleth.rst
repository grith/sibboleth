:mod:`~arcs.shibboleth.client.shibboleth` -- urllib shibboleth authentication
=============================================================================

.. _ref-shibboleth

.. module:: arcs.shibboleth.client.shibboleth
.. moduleauthor:: Russell Sim <russell@vpac.org>


:class:`Shibboleth` Objects
---------------------------

Using the shibboleth handler is a bit different to the urllib2 handlers because the shibboleth auth chain is far more complex.

::

    from arcs.shibboleth.client import Shibboleth, SimpleCredentialManager, Idp
    idp = Idp('VPAC')
    c = SimpleCredentialManager('testuser', 'testpass')
    shibboleth = Shibboleth(idp, c)
    response = shibboleth.openurl('https://slcs1.arcs.org.au/SLCS/login')
    for line in response:
        print line


To manually specify proxies, use

::

    proxies = {'http': 'http://user1:pass@localhost:3128/'}
    shibboleth = Shibboleth(idp, c, proxies=proxies)


.. autoclass:: Shibboleth
   :members:
   :undoc-members:


:class:`ShibbolethHandler` Objects
----------------------------------
.. autoclass:: ShibbolethHandler
   :members:
   :undoc-members:


:class:`ShibbolethAuthHandler` Objects
--------------------------------------
.. autoclass:: ShibbolethAuthHandler
   :members:
   :undoc-members:


:func:`set_cookies_expires` Function
----------------------------------------
.. autofunction:: set_cookies_expiries
