package grith.sibboleth;

import org.python.core.Py;
import org.python.core.PyObject;

/**
 * An implementation of an {@link CredentialManager} that can be used from
 * within graphical user interfaces to login to a shib instance.
 * 
 * You'd create it after a user clicks a "Submit" button and populate it with
 * the username and password of the users choice.
 * 
 * @author Markus Binsteiner
 * 
 */
public class OneTimeStaticCredentialManager implements CredentialManager {

	private boolean usernameAndPasswordAlreadyRead = false;
	private final char[] password;
	private final String username;

	public OneTimeStaticCredentialManager(String username, char[] password) {

		this.password = password;
		this.username = username;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see grith.sibboleth.CredentialManager#get_password()
	 */
	public String get_password() {
		return new String(password);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see grith.sibboleth.CredentialManager#get_username()
	 */
	public String get_username() {
		return username;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see grith.sibboleth.CredentialManager#prompt(java.lang.Object)
	 */
	public PyObject prompt(Object response) {

		if (usernameAndPasswordAlreadyRead) {
			throw new CredentialManagerException(
			"Login failed. Probably wrong username and/or password.");
		}
		usernameAndPasswordAlreadyRead = true;
		return Py.java2py(response).invoke("run");

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see grith.sibboleth.CredentialManager#set_title(java.lang.String)
	 */
	public void set_title(String title) {
	}

}
