package au.org.arcs.auth.shibboleth;

import org.python.core.PyInstance;

public interface ShibbolethClient {
	
	public PyInstance shibopen( String url, String username, String password, String idp);
	
	public PyInstance open(String url);

}
