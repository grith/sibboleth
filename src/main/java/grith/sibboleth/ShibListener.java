package grith.sibboleth;

import org.python.core.PyInstance;

/**
 * Interface that can be used to monitor the login process.
 * 
 * Might be useful for graphical user interfaces. You'd connect it using the
 * {@link Shibboleth#addShibListener(ShibListener)} method.
 * 
 * @author Markus Binsteiner
 * 
 */
public interface ShibListener {

	/**
	 * Fired when shib login is complete.
	 * 
	 * @param response the response as a {@link PyInstance} object
	 */
	public void shibLoginComplete(PyInstance response);

	/**
	 * Fired when something during the shib login process failed.
	 * 
	 * @param e the exception
	 */
	public void shibLoginFailed(Exception e);

	/**
	 * Fired when shib login process starts.
	 * 
	 * Don't rely on this method to be called. Only the swing proxy classes fire
	 * it.
	 */
	public void shibLoginStarted();

}
