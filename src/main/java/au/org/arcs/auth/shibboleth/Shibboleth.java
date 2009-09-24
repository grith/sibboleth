package au.org.arcs.auth.shibboleth;

import java.util.Enumeration;
import java.util.Iterator;
import java.util.Vector;

import org.python.core.Py;
import org.python.core.PyInstance;
import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

public class Shibboleth {

	private final ShibbolethClient shibClient;
	
	private PyInstance response = null;

	public Shibboleth(IdpObject idp, CredentialManager cm) {

		PythonInterpreter interpreter = new PythonInterpreter();
		interpreter
				.exec("from arcs.shibboleth.client.shibboleth import Shibboleth");
		PyObject shibbolethClientClass = interpreter.get("Shibboleth");

		PyObject shibObject = shibbolethClientClass.__call__(Py.java2py(idp), Py.java2py(cm));
		shibClient = (ShibbolethClient) shibObject.__tojava__(ShibbolethClient.class);
		
		shibClient.add_listener(Py.java2py(this).__getattr__("shibLoginComplete"));
	}



	public PyInstance openurl(String url) {

		return shibClient.openurl(url);
	}

	public static void main(String[] args) throws InterruptedException {

		java.security.Security.addProvider(new ArcsSecurityProvider());

		java.security.Security.setProperty("ssl.TrustManagerFactory.algorithm",
				"TrustAllCertificates");

		IdpObject idp = new StaticIdpObject("VPAC");
		CredentialManager cm = new StaticCredentialManager(args[0], args[1]);
		
		Shibboleth shib = new Shibboleth(idp, cm);

		String url = "https://slcs1.arcs.org.au/SLCS/login";
		PyInstance returnValue = shib.openurl(url);

		System.out.println("Finished.");


	}
	
	public PyInstance getResponse() {
		return response;
	}
	

	public String getResponseAsString() {
		
		Iterable<PyObject> it = response.asIterable();
		
		StringBuffer responseString = new StringBuffer();
		
		for (Iterator i = it.iterator(); i.hasNext();) {
			responseString.append(i.next());
		}
		
		return responseString.toString();
	}


	public void shibLoginComplete() {
		response = shibClient.get_response(); 
		
		fireShibLoginComplete(getResponse());
	}
	
	// Event stuff
	
	private Vector<ShibListener> shibListeners;

	private void fireShibLoginComplete(PyInstance response) {

		if (shibListeners != null && !shibListeners.isEmpty()) {

			// make a copy of the listener list in case
			// anyone adds/removes mountPointsListeners
			Vector<ShibListener> shibChangeTargets;
			synchronized (this) {
				shibChangeTargets = (Vector<ShibListener>) shibListeners
						.clone();
			}

			// walk through the listener list and
			// call the gridproxychanged method in each
			Enumeration<ShibListener> e = shibChangeTargets.elements();
			while (e.hasMoreElements()) {
				ShibListener valueChanged_l = (ShibListener) e.nextElement();
				valueChanged_l.shibLoginComplete(response);
			}
		}
	}

	// register a listener
	synchronized public void addShibListener(ShibListener l) {
		if (shibListeners == null)
			shibListeners = new Vector<ShibListener>();
		shibListeners.addElement(l);
	}

	// remove a listener
	synchronized public void removeShibListener(ShibListener l) {
		if (shibListeners == null) {
			shibListeners = new Vector<ShibListener>();
		}
		shibListeners.removeElement(l);
	}

}
