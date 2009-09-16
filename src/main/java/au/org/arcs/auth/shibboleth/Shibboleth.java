package au.org.arcs.auth.shibboleth;

import java.util.Iterator;

import org.python.core.PyInstance;
import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

public class Shibboleth {

	private final ShibbolethClient shibClient;
	
	private final String url;
	
    public Shibboleth(String url) {
    	this.url = url;
        PythonInterpreter interpreter = new PythonInterpreter();
        interpreter.exec("from arcs.shibboleth.client.shibboleth import Shibboleth");
        PyObject shibbolethClientClass = interpreter.get("Shibboleth");
        PyObject shibObject = shibbolethClientClass.__call__();
        shibClient = (ShibbolethClient)shibObject.__tojava__(ShibbolethClient.class);
    }

    public PyInstance shibOpen(String username, char[] password, IdpObject idp) {
    	
    	return shibClient.shibopen(url, username, new String(password), idp);
    	
    }

    public PyInstance open() {
    	
    	return shibClient.open(url);
    }
	
    
    public static void main(String[] args) {
    	
    	java.security.Security.addProvider(new ArcsSecurityProvider());

    	java.security.Security.setProperty("ssl.TrustManagerFactory.algorithm", "TrustAllCertificates");
    	
    	Shibboleth shib = new Shibboleth("https://slcs1.arcs.org.au/SLCS/login");
    	
    	PyInstance returnValue = shib.shibOpen(args[0], args[1].toCharArray(), new IdpObject());
    	
    	Iterable<PyObject> it = returnValue.asIterable();
    	
    	for ( Iterator i = it.iterator(); i.hasNext(); ) {
    		
    		System.out.println(i.next());
    		
    	}
    	
    	returnValue = shib.open();
    	
    	it = returnValue.asIterable();
    	
    	for ( Iterator i = it.iterator(); i.hasNext(); ) {
    		
    		System.out.println(i.next());
    		
    	}
    	
    	
    }
	

}
