package au.org.arcs.auth.shibboleth;

import java.util.Map;

public class StaticIdpObject implements IdpObject {

	private final String idpName;
	
	public StaticIdpObject(String idpName) {
		this.idpName = idpName;
	}
	
	public void choose_idp() {
		// do nothing
	}

	public String get_idp() {
		return idpName;
	}

	public void set_idps(Map idps) {
		// do nothing
	}

}
