package au.org.arcs.auth.shibboleth;

import org.python.core.PyInstance;

public class StaticIdpObject extends IdpObject {

	private final String idpName;
	
	public StaticIdpObject(String idpName) {
		this.idpName = idpName;
	}
	

	public String get_idp() {
		return idpName;
	}

	public PyInstance prompt(ShibbolethClient shibboleth) {
		shibboleth.run();
		return null;
	}

}
