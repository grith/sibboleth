package grith.sibboleth;

/**
 * Used for the (j/p)ython - Java wrapping. Don't worry.
 * 
 * @author Markus Binsteiner
 * 
 */
public interface ShibLoginEventSource {

	public void addShibListener(ShibListener l);

	public void removeShibListener(ShibListener l);

}
