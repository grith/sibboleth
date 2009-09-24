package au.org.arcs.auth.shibboleth;

import org.python.core.PyInstance;

public interface ShibListener {
	
	public void shibLoginComplete(PyInstance response);
	
}
