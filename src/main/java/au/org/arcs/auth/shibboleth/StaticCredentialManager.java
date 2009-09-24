package au.org.arcs.auth.shibboleth;

import org.python.core.PyInstance;

public class StaticCredentialManager implements CredentialManager {
	
	private String password;
	private String username;
	
	public StaticCredentialManager(String username, String password) {
		
		this.password = password;
		this.username = username;
	}

	public String get_password() {
		System.out.println("get password");
		return password;
	}

	public String get_username() {
		System.out.println("get username");
		return username;
	}

	public PyInstance prompt(ShibbolethClient shibboleth) {

		System.out.println("Credentialmanager prompt.");
		
		shibboleth.run();
		
		return null;

	}

	public void set_title(String title) {
		
		System.out.println(title);
	}

}
