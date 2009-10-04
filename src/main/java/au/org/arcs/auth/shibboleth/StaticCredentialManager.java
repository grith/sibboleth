package au.org.arcs.auth.shibboleth;

import org.python.core.PyInstance;

public class StaticCredentialManager implements CredentialManager {
	
	private char[] password;
	private String username;
	
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

	public PyInstance prompt(ShibbolethClient shibboleth) {

		shibboleth.run();
		return null;

	}

	public void set_title(String title) {
		// 
	}

}
