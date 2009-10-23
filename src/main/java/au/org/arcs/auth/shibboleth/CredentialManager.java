package au.org.arcs.auth.shibboleth;

import org.python.core.PyInstance;
import org.python.core.PyObject;

public interface CredentialManager {
	
	public String get_password();
	
	public String get_username();
	
	public PyObject prompt(Object shibboleth);
	
	public void set_title(String title);

}
