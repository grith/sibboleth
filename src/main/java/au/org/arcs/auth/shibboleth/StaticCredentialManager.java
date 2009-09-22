package au.org.arcs.auth.shibboleth;

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

	public void prompt(ShibbolethClient shibboleth) {

		System.out.println("Credentialmanager prompt.");
		
		shibboleth.run();

	}

	public void set_title(String title) {
		
		System.out.println(title);
	}

}
