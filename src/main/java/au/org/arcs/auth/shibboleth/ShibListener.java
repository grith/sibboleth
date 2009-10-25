package au.org.arcs.auth.shibboleth;

import org.python.core.PyInstance;

public interface ShibListener {
	
	
	/**
	 * Fired when shib login process starts.
	 * 
	 * Don't rely on this method to be called. Only the swing proxy classes fire it.
	 */
	public void shibLoginStarted();
	
	public void shibLoginComplete(PyInstance response);
	
	public void shibLoginFailed(Exception e);

}
