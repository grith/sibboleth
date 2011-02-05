package grith.sibboleth;

import org.python.core.Py;
import org.python.core.PyObject;

/**
 * An implementation of an {@link CredentialManager} that can be used from
 * within, for example, commandline user interfaces to login to a shib instance.
 * 
 * @author Markus Binsteiner
 * 
 */
public class StaticCredentialManager implements CredentialManager {

	private final char[] password;
	private final String username;

	/**
	 * Creates an instance and loads the shib username and password.
	 * 
	 * @param username
	 *            the username
	 * @param password
	 *            the password
	 */
	public StaticCredentialManager(String username, char[] password) {

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

		// Py.java2py(response).__call__(Py.java2py("run"));
		return Py.java2py(response).invoke("run");
		// shibboleth.run();
		// return null;

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see grith.sibboleth.CredentialManager#set_title(java.lang.String)
	 */
	public void set_title(String title) {
		//
	}

}
