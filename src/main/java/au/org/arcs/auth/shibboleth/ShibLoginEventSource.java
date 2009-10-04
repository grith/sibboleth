package au.org.arcs.auth.shibboleth;

public interface ShibLoginEventSource {
	
	public void addShibListener(ShibListener l);
	public void removeShibListener(ShibListener l);

}
