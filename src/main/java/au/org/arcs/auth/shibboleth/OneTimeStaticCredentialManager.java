package au.org.arcs.auth.shibboleth;

import org.python.core.PyInstance;

public class OneTimeStaticCredentialManager implements CredentialManager {
	
	private boolean usernameAndPasswordAlreadyRead = false;
	private char[] password;
	private String username;
	
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

	public PyInstance prompt(ShibbolethClient shibboleth) {

		if ( usernameAndPasswordAlreadyRead ) {
			throw new CredentialManagerException("Login failed. Probably wrong username and/or password.");
		}
		usernameAndPasswordAlreadyRead = true;
		shibboleth.run();
		return null;

	}

	public void set_title(String title) {
		// 
	}

}
