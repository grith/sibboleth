package au.org.arcs.auth.shibboleth;

import org.python.core.PyInstance;


public class DummyIdpObject extends IdpObject {
	
	private String sel = "Dummy";

	@Override
	public String get_idp() {
		return sel;
	}
	
	@Override
	public PyInstance prompt(ShibbolethClient shibboleth) {
		return null;
	}

}
