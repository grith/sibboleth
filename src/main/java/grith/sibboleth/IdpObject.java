package grith.sibboleth;

import grisu.jcommons.interfaces.IdpListener;

import java.util.Enumeration;
import java.util.Map;
import java.util.SortedSet;
import java.util.TreeSet;
import java.util.Vector;

import org.python.core.PyInstance;

/**
 * Along with the {@link Shibboleth} and {@link CredentialManager}
 * classes/interfaces a central part of sibboleth, it holds a list of IdPs and
 * traverses through levels of IdPs as the user navigates through them.
 * 
 * @author Markus Binsteiner
 */
public abstract class IdpObject {

	protected SortedSet<String> idpList = null;

	// event stuff
	private Vector<IdpListener> idpListeners;

	/**
	 * Adds an {@link IdpListener}.
	 * 
	 * @param l
	 *            the listener
	 */
	synchronized public void addIdpListener(IdpListener l) {
		if (idpListeners == null) {
			idpListeners = new Vector<IdpListener>();
		}
		idpListeners.addElement(l);
	}

	private void fireIdpListSet() {

		if ((idpListeners != null) && !idpListeners.isEmpty()) {

			Vector<IdpListener> shibChangeTargets;
			synchronized (this) {
				shibChangeTargets = (Vector<IdpListener>) idpListeners.clone();
			}

			Enumeration<IdpListener> e = shibChangeTargets.elements();
			while (e.hasMoreElements()) {
				IdpListener valueChanged_l = e.nextElement();
				valueChanged_l.idpListLoaded(this.idpList);
			}
		}

	}

	/**
	 * Returns either a static or user-selected IdP.
	 * 
	 * @return the IdP name (should be in the list of currently loaded IdPs)
	 */
	public abstract String get_idp();

	/**
	 * Returns the list of currently loaded IdPs
	 * 
	 * @return the IdP names
	 */
	public SortedSet<String> getIdps() {
		return this.idpList;
	}

	/**
	 * Called internally from within Python. Don't worry about it.
	 * 
	 * @param shibboleth
	 *            the controller object
	 * @return the remote response
	 */
	public abstract PyInstance prompt(ShibbolethClient shibboleth);

	/**
	 * Removes an {@link IdpListener}.
	 * 
	 * @param l
	 *            the listener to remove
	 */
	synchronized public void removeIdpListener(IdpListener l) {
		if (idpListeners == null) {
			idpListeners = new Vector<IdpListener>();
		}
		idpListeners.removeElement(l);
	}

	/**
	 * Called from within python to populate the internal Idp-list.
	 * 
	 * Do not call that manually.
	 * 
	 * @param idps
	 *            the list of Idps
	 */
	public void set_idps(Map<String, String> idps) {

		this.idpList = new TreeSet<String>(idps.keySet());

		fireIdpListSet();
	}

}