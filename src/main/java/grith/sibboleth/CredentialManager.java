package grith.sibboleth;

import org.python.core.PyObject;

/**
 * An interface to be able to connect to the {@code CredentialManager} Python
 * object from the {@code sibboleth.credentials} module.
 * 
 * Used to hold a username and password or to ask the user (interactively) for
 * those.
 * 
 * @author Markus Binsteiner/Russel Sim
 * 
 */
public interface CredentialManager {

	/**
	 * Returns the users password.
	 * 
	 * @return the password
	 */
	public String get_password();

	/**
	 * Returns the users username.
	 * 
	 * @return the username
	 */
	public String get_username();

	/**
	 * Called internally from within Python. Don't worry about it.
	 * 
	 * @param shibboleth
	 *            the controller object
	 * @return
	 */
	public PyObject prompt(Object shibboleth);

	/**
	 * Shows the title of the Basic Auth or Form that the user is presented
	 * with.
	 * 
	 * Called whenever sibbloeth hits one of those forms.
	 * 
	 * @param title
	 *            the title
	 */
	public void set_title(String title);

}
