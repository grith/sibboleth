package grith.sibboleth;

import org.python.core.Py;
import org.python.core.PyObject;

public class StaticCredentialManager implements CredentialManager {

	private final char[] password;
	private final String username;

	public StaticCredentialManager(String username, char[] password) {

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

		// Py.java2py(response).__call__(Py.java2py("run"));
		return Py.java2py(response).invoke("run");
		// shibboleth.run();
		// return null;

	}

	public void set_title(String title) {
		//
	}

}
