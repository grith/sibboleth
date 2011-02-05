package grith.sibboleth;

import org.python.core.PyInstance;

/**
 * Dummy implementation of a {@link CredentialManager}.
 * 
 * Used usually when you don't want to login but display a list of available
 * IdPs to display to the user in a UI.
 * 
 * @author Markus Binsteiner
 * 
 */
public class DummyCredentialManager implements CredentialManager {

	public String get_password() {
		return null;
	}

	public String get_username() {
		return null;
	}

	public PyInstance prompt(Object response) {
		return null;
	}

	public void set_title(String title) {
	}

}
