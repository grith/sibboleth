"""
Hack the ssl class in socket.py NOT to enable all supported ciphersuits when
setting up an SSL connection.

Replace the _make_ssl_socket method from socket.ssl class with our own version
that does not enable all ciphersuits that Java lists as supported.

Because socket.py hides the real ssl class as _realssl, use that name to
replace the method.
"""

import socket
import java.net.Socket
import javax.net.ssl.SSLSocketFactory

def _make_ssl_socket_sslonlydefaultciphers(self, plain_socket, auto_close=0):
        java_net_socket = plain_socket._get_jsocket()
        assert isinstance(java_net_socket, java.net.Socket)
        host = java_net_socket.getInetAddress().getHostAddress()
        port = java_net_socket.getPort()
        factory = javax.net.ssl.SSLSocketFactory.getDefault();
        ssl_socket = factory.createSocket(java_net_socket, host, port, auto_close)
        #ssl_socket.setEnabledCipherSuites(ssl_socket.getSupportedCipherSuites())
        ssl_socket.startHandshake()
        return ssl_socket

# replace the _make_ssl_socket method in the ssl class with our custom
# note: socket.py hides ssl as _realssl 

socket._realssl._make_ssl_socket = _make_ssl_socket_sslonlydefaultciphers

