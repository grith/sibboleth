package au.org.arcs.auth.shibboleth;

import java.util.Enumeration;
import java.util.Map;
import java.util.SortedSet;
import java.util.TreeSet;
import java.util.Vector;

import org.python.core.PyInstance;

import au.org.arcs.jcommons.interfaces.IdpListener;

public abstract class IdpObject {
	
	protected SortedSet<String> idpList = null;

	public abstract PyInstance prompt(ShibbolethClient shibboleth);

	public abstract String get_idp();

	public void set_idps(Map<String, String> idps) {
		
		this.idpList = new TreeSet<String>(idps.keySet());
		
		fireIdpListSet();
	}
	
	public SortedSet<String> getIdps() {
		return this.idpList;
	}

	
	
	// event stuff
	private Vector<IdpListener> idpListeners;
	
	
	private void fireIdpListSet() {
		
		if (idpListeners != null && !idpListeners.isEmpty()) {

			Vector<IdpListener> shibChangeTargets;
			synchronized (this) {
				shibChangeTargets = (Vector<IdpListener>) idpListeners
						.clone();
			}

			Enumeration<IdpListener> e = shibChangeTargets.elements();
			while (e.hasMoreElements()) {
				IdpListener valueChanged_l = e.nextElement();
				valueChanged_l.idpListLoaded(this.idpList);
			}
		}
		
	}
	
	// register a listener
	synchronized public void addIdpListener(IdpListener l) {
		if (idpListeners == null)
			idpListeners = new Vector<IdpListener>();
		idpListeners.addElement(l);
	}

	// remove a listener
	synchronized public void removeIdpListener(IdpListener l) {
		if (idpListeners == null) {
			idpListeners = new Vector<IdpListener>();
		}
		idpListeners.removeElement(l);
	}

}