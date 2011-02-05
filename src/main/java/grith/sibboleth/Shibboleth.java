package grith.sibboleth;

import grisu.jcommons.utils.DefaultGridSecurityProvider;
import grisu.jcommons.utils.NewHttpProxyEvent;

import java.util.Enumeration;
import java.util.Vector;

import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;
import org.bushe.swing.event.EventBus;
import org.bushe.swing.event.EventSubscriber;
import org.bushe.swing.event.Prioritized;
import org.python.core.Py;
import org.python.core.PyInstance;
import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

/**
 * Central wrapper class that imports the {@code Shibboleth} class from the
 * {@code sibboleth.shibboleth.py} python module.
 * 
 * Encapsulates the whole redirect-flow that happens when you do a shibboleth
 * authentication.
 * 
 * @author Markus Binsteiner
 * 
 */
public class Shibboleth implements ShibLoginEventSource,
EventSubscriber<NewHttpProxyEvent>, Prioritized {

	static final Logger myLogger = Logger.getLogger(Shibboleth.class.getName());

	/**
	 * Convenience class to activate an All-trusting Trustmanager. Most useful
	 * for testing.
	 */
	public static void initDefaultSecurityProvider() {

		java.security.Security.addProvider(new DefaultGridSecurityProvider());

		java.security.Security.setProperty("ssl.TrustManagerFactory.algorithm",
		"TrustAllCertificates");
	}

	public static void main(String[] args) throws InterruptedException {

		myLogger.debug("Test debug");

		java.security.Security.addProvider(new DefaultGridSecurityProvider());

		java.security.Security.setProperty("ssl.TrustManagerFactory.algorithm",
		"TrustAllCertificates");

		IdpObject idp = new StaticIdpObject("The University of Auckland");

		CredentialManager cm = new StaticCredentialManager(args[0],
				args[1].toCharArray());

		Shibboleth shib = new Shibboleth(idp, cm);
		shib.addShibListener(new ShibListener() {

			public void shibLoginComplete(PyInstance response) {

				Iterable<PyObject> it = response.asIterable();

				StringBuffer responseString = new StringBuffer();

				for (Object element : it) {
					responseString.append(element);
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

	/**
	 * Convenience method to tell the (j/p)ython and the Java code to use a
	 * specific http prpxoy server.
	 * 
	 * @param host
	 *            the http proxy server host
	 * @param port
	 *            the http proxy server port
	 * @param username
	 *            the http proxy server username (or null if non-authenticated)
	 * @param password
	 *            the http proxy server password (or null if non-authenticated)
	 */
	public static void setHttpProxy(String host, int port, String username,
			char[] password) {

		String proxyString = null;

		try {

			if (StringUtils.isBlank(host)) {
				proxyString = "";
			} else {
				if (StringUtils.isBlank(username)) {
					proxyString = "http://" + host + ":" + port;
				} else {
					proxyString = "http://" + username + ":"
					+ new String(password) + "@" + host + ":" + port;
				}
			}

			PythonInterpreter interpreter = new PythonInterpreter();

			interpreter.exec("import os");
			interpreter.exec("os.putenv('http_proxy', " + "\"" + proxyString
					+ "\") ");
			interpreter.exec("os.putenv('https_proxy', " + "\"" + proxyString
					+ "\") ");

		} catch (Exception e) {
			e.printStackTrace();
		}

	}

	private final ShibbolethClient shibClient;

	private PyInstance response = null;

	private Vector<ShibListener> shibListeners;

	public Shibboleth(IdpObject idp, CredentialManager cm) {

		EventBus.subscribe(NewHttpProxyEvent.class, this);

		PythonInterpreter interpreter = new PythonInterpreter();
		interpreter
		.exec("from sibboleth import Shibboleth");
		PyObject shibbolethClientClass = interpreter.get("Shibboleth");

		PyObject shibObject = shibbolethClientClass.__call__(Py.java2py(idp),
				Py.java2py(cm));
		shibClient = (ShibbolethClient) shibObject
		.__tojava__(ShibbolethClient.class);

		shibClient.add_listener(Py.java2py(this).__getattr__(
		"shibLoginComplete"));
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * grith.sibboleth.ShibLoginEventSource#addShibListener(grith.sibboleth.
	 * ShibListener)
	 */
	synchronized public void addShibListener(ShibListener l) {
		if (shibListeners == null) {
			shibListeners = new Vector<ShibListener>();
		}
		shibListeners.addElement(l);
	}

	private void fireIdpsLoaded(PyInstance response) {

		if ((shibListeners != null) && !shibListeners.isEmpty()) {

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
				ShibListener valueChanged_l = e.nextElement();
				valueChanged_l.shibLoginComplete(response);
			}
		}
	}

	// Event stuff

	private void fireShibLoginComplete(PyInstance response) {

		if ((shibListeners != null) && !shibListeners.isEmpty()) {

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
				ShibListener valueChanged_l = e.nextElement();
				valueChanged_l.shibLoginComplete(response);
			}
		}
	}

	private void fireShibLoginFailed(Exception ex) {

		if ((shibListeners != null) && !shibListeners.isEmpty()) {

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
				ShibListener valueChanged_l = e.nextElement();
				valueChanged_l.shibLoginFailed(ex);
			}
		}

	}

	private void fireShibLoginStarted() {

		if ((shibListeners != null) && !shibListeners.isEmpty()) {

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
				ShibListener valueChanged_l = e.nextElement();
				valueChanged_l.shibLoginStarted();
			}
		}

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.bushe.swing.event.Prioritized#getPriority()
	 */
	public int getPriority() {
		return -100;
	}

	/**
	 * Returns the last response in the sequence of shib-calls/redirects.
	 * 
	 * Needed, for example, to request a slcs certificate with the
	 * {@code gsindl} package.
	 * 
	 * @return the response as an {@link PyInstance} object
	 */
	public PyInstance getResponse() {
		return response;
	}

	/**
	 * Convenience method to get last response in its String representation.
	 * 
	 * @return the response as a String
	 */
	public String getResponseAsString() {

		Iterable<PyObject> it = response.asIterable();

		StringBuffer responseString = new StringBuffer();

		for (Object element : it) {
			responseString.append(element);
		}

		return responseString.toString();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.bushe.swing.event.EventSubscriber#onEvent(java.lang.Object)
	 */
	public void onEvent(NewHttpProxyEvent arg0) {

		setHttpProxy(arg0.getProxyHost(), arg0.getProxyPort(),
				arg0.getUsername(), arg0.getPassword());

	}

	/**
	 * 
	 * 
	 * @param url
	 * @return
	 */
	public PyInstance openurl(String url) {

		try {
			return shibClient.openurl(url);
		} catch (CredentialManagerException e) {
			fireShibLoginFailed(e);
			return null;
		}
	}

	// remove a listener
	synchronized public void removeShibListener(ShibListener l) {
		if (shibListeners == null) {
			shibListeners = new Vector<ShibListener>();
		}
		shibListeners.removeElement(l);
	}

	public void shibLoginComplete() {
		response = shibClient.get_response();

		fireShibLoginComplete(getResponse());
	}

}
