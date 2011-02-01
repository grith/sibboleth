package grith.sibboleth;


public interface ShibLoginEventSource {

	public void addShibListener(ShibListener l);

	public void removeShibListener(ShibListener l);

}
