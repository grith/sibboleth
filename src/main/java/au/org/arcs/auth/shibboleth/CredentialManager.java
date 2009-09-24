package au.org.arcs.auth.shibboleth;

import org.python.core.PyInstance;

public interface CredentialManager {
	
	public String get_password();
	
	public String get_username();
	
	public PyInstance prompt(ShibbolethClient shibboleth);
	
	public void set_title(String title);

}
