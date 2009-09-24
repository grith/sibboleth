package au.org.arcs.auth.shibboleth;

import java.util.Iterator;

import org.python.core.PyInstance;
import org.python.core.PyObject;

public interface ShibbolethClient {
	
//	public PyInstance shibopen( String url, String username, String password, IdpObject idp );
	
	public PyInstance openurl(String url);
	
	public PyInstance run();
	
	public void add_listener(PyObject listener);
	
	public PyInstance get_response();
	
}
