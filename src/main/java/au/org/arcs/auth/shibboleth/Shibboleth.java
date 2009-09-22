package au.org.arcs.auth.shibboleth;

import java.security.Security;
import java.util.Iterator;

import org.python.core.Py;
import org.python.core.PyInstance;
import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

public class Shibboleth {

	private final ShibbolethClient shibClient;

	public Shibboleth(IdpObject idp, CredentialManager cm) {


		PythonInterpreter interpreter = new PythonInterpreter();
		interpreter
				.exec("from arcs.shibboleth.client.shibboleth import Shibboleth");
		PyObject shibbolethClientClass = interpreter.get("Shibboleth");

		PyObject shibObject = shibbolethClientClass.__call__(Py.java2py(idp), Py.java2py(cm));
		shibClient = (ShibbolethClient) shibObject.__tojava__(ShibbolethClient.class);
	}



	public PyInstance openurl(String url) {

		return shibClient.openurl(url);
	}

	public static void main(String[] args) {

		java.security.Security.addProvider(new ArcsSecurityProvider());

		java.security.Security.setProperty("ssl.TrustManagerFactory.algorithm",
				"TrustAllCertificates");

		IdpObject idp = new StaticIdpObject("VPAC");
		CredentialManager cm = new StaticCredentialManager(args[0], args[1]);
		
		Shibboleth shib = new Shibboleth(idp, cm);

		String url = "https://slcs1.arcs.org.au/SLCS/login";
		PyInstance returnValue = shib.openurl(url);

		Iterable<PyObject> it = returnValue.asIterable();

		for (Iterator i = it.iterator(); i.hasNext();) {

			System.out.println(i.next());

		}



	}

}
