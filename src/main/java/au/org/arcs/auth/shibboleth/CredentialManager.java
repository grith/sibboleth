package au.org.arcs.auth.shibboleth;

public interface CredentialManager {
	
	public String get_password();
	
	public String get_username();
	
	public void prompt(ShibbolethClient shibboleth);
	
	public void set_title(String title);

}
