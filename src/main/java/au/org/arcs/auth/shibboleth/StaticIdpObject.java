package au.org.arcs.auth.shibboleth;

import java.util.Map;

import org.python.core.Py;
import org.python.core.PyInstance;

public class StaticIdpObject implements IdpObject {

	private final String idpName;
	
	public StaticIdpObject(String idpName) {
		this.idpName = idpName;
	}
	

	public String get_idp() {
		return idpName;
	}

	public void set_idps(Map<String, String> idps) {
		//
	}

	public PyInstance prompt(ShibbolethClient shibboleth) {
		shibboleth.run();
		return null;
	}

}
