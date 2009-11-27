package au.org.arcs.auth.shibboleth;

import java.util.Enumeration;
import java.util.Iterator;
import java.util.Vector;

import org.apache.commons.httpclient.ProxyHost;
import org.apache.commons.lang.StringUtils;
import org.bushe.swing.event.EventBus;
import org.bushe.swing.event.EventSubscriber;
import org.bushe.swing.event.Prioritized;
import org.python.core.Py;
import org.python.core.PyInstance;
import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

import au.org.arcs.jcommons.utils.ArcsSecurityProvider;
import au.org.arcs.jcommons.utils.NewHttpProxyEvent;

public class Shibboleth implements ShibLoginEventSource, EventSubscriber<NewHttpProxyEvent>, Prioritized {
	
	public static void initDefaultSecurityProvider() {
		
		java.security.Security.addProvider(new ArcsSecurityProvider());

		java.security.Security.setProperty("ssl.TrustManagerFactory.algorithm",
				"TrustAllCertificates");
	}

	private final ShibbolethClient shibClient;
	
	private PyInstance response = null;

	public Shibboleth(IdpObject idp, CredentialManager cm) {
		
		EventBus.subscribe(NewHttpProxyEvent.class, this);

		PythonInterpreter interpreter = new PythonInterpreter();
		interpreter
				.exec("from arcs.shibboleth.client.shibboleth import Shibboleth");
		PyObject shibbolethClientClass = interpreter.get("Shibboleth");

		PyObject shibObject = shibbolethClientClass.__call__(Py.java2py(idp), Py.java2py(cm));
		shibClient = (ShibbolethClient) shibObject.__tojava__(ShibbolethClient.class);
		
		shibClient.add_listener(Py.java2py(this).__getattr__("shibLoginComplete"));
	}



	public PyInstance openurl(String url) {

		try {
			return shibClient.openurl(url);
		} catch (CredentialManagerException e) {
			fireShibLoginFailed(e);
			return null;
		}
	}
	
	private void fireShibLoginFailed(Exception ex) {
		
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
				valueChanged_l.shibLoginFailed(ex);
			}
		}
		
	}

	public static void main(String[] args) throws InterruptedException {

		java.security.Security.addProvider(new ArcsSecurityProvider());

		java.security.Security.setProperty("ssl.TrustManagerFactory.algorithm",
				"TrustAllCertificates");

		IdpObject idp = new StaticIdpObject("VPAC");
		
		CredentialManager cm = new StaticCredentialManager(args[0], args[1].toCharArray());
		
		Shibboleth shib = new Shibboleth(idp, cm);
		shib.addShibListener(new ShibListener() {
			
			public void shibLoginComplete(PyInstance response) {

				Iterable<PyObject> it = response.asIterable();
				
				StringBuffer responseString = new StringBuffer();
				
				for (Iterator i = it.iterator(); i.hasNext();) {
					responseString.append(i.next());
				}
				
				System.out.println(responseString.toString());
				
				
			}

			public void shibLoginFailed(Exception e) {

				e.printStackTrace();
				
			}

			public void shibLoginStarted() {

				System.out.println("Shib login started.");
			}
		});

		String url = "https://slcs1.arcs.org.au/SLCS/login";
		PyInstance returnValue = shib.openurl(url);
		
		System.out.println(shib.getResponseAsString());

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
	
	private void fireShibLoginStarted() {
		
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
				valueChanged_l.shibLoginStarted();
			}
		}
		
	}

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
	
	
	private void fireIdpsLoaded(PyInstance response) {

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



	public void onEvent(NewHttpProxyEvent arg0) {
		// TODO Auto-generated method stub
		PythonInterpreter interpreter = new PythonInterpreter();
		
		String proxyString = null;
		
		try {
		
		if ( StringUtils.isBlank(arg0.getProxyHost()) ) {
			proxyString = "";
		} else {	
			if ( StringUtils.isBlank(arg0.getUsername()) ) {
				proxyString = "http://"+arg0.getProxyHost()+":"+arg0.getProxyPort();
			} else {
				proxyString = "http://"+arg0.getUsername()+":"+new String(arg0.getPassword())+"@"+arg0.getProxyHost()+":"+arg0.getProxyPort();
			}
		}
		interpreter.exec("import os");
		interpreter.exec("os.putenv('http_proxy', "+"\""+proxyString+"\") ");
		interpreter.exec("os.putenv('https_proxy', "+"\""+proxyString+"\") ");
		
		} catch (Exception e) {
			e.printStackTrace();
		}
		


	}



	public int getPriority() {
		return -100;
	}

}
