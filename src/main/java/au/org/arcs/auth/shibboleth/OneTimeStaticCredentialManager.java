package au.org.arcs.auth.shibboleth;

import org.python.core.Py;
import org.python.core.PyObject;

public class OneTimeStaticCredentialManager implements CredentialManager {

	private boolean usernameAndPasswordAlreadyRead = false;
	private final char[] password;
	private final String username;

	public OneTimeStaticCredentialManager(String username, char[] password) {

		this.password = password;
		this.username = username;
	}

	public String get_password() {
		return new String(password);
	}

	public String get_username() {
		return username;
	}

	public PyObject prompt(Object response) {

		if ( usernameAndPasswordAlreadyRead ) {
			throw new CredentialManagerException("Login failed. Probably wrong username and/or password.");
		}
		usernameAndPasswordAlreadyRead = true;
		return Py.java2py(response).invoke("run");
		//		Py.java2py(response).__call__(Py.java2py("run"));
		//		shibboleth.run();
		//		return null;

	}

	public void set_title(String title) {
		//
	}

}
