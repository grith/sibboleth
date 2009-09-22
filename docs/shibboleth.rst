:mod:`~arcs.shibboleth.client.shibboleth` -- urllib shibboleth authentication
=============================================================================

.. _ref-shibboleth

.. module:: arcs.shibboleth.client.shibboleth
.. moduleauthor:: Russell Sim <russell@vpac.org>


:class:`Shibboleth` Objects
---------------------------

Using the shibboleth handler is a bit different to the urllib2 handlers because the shibboleth auth chain is far more complex.

::

    from arcs.shibboleth.client import Shibboleth, CredentialManager, Idp
    idp = Idp()
    c = CredentialManager()
    shibboleth = Shibboleth(idp, c, cj)
    response = shibboleth.openurl(sp)

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
