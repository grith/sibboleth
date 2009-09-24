package au.org.arcs.auth.shibboleth;

import java.util.Map;

import org.python.core.Py;
import org.python.core.PyInstance;

public class StaticIdpObject implements IdpObject {

	private final String idpName;
	
	public StaticIdpObject(String idpName) {
		System.out.println("IDP constructor");
		this.idpName = idpName;
	}
	

	public String get_idp() {
		System.out.println("GetIdp");		
		return idpName;
	}

	public void set_idps(Map<String, String> idps) {
		// do nothing
		System.out.println("Set idp");
	}

	public PyInstance prompt(ShibbolethClient shibboleth) {
		
		System.out.println("Idp prompt");
		shibboleth.run();
		return null;
		
	}

}
