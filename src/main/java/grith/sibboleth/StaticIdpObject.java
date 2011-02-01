package grith.sibboleth;

import org.python.core.PyInstance;

public class StaticIdpObject extends IdpObject {

	private final String idpName;

	public StaticIdpObject(String idpName) {
		this.idpName = idpName;
	}

	@Override
	public String get_idp() {
		return idpName;
	}

	@Override
	public PyInstance prompt(ShibbolethClient shibboleth) {
		shibboleth.run();
		return null;
	}

}
