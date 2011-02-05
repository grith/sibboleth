package grith.sibboleth;

import org.python.core.PyInstance;

/**
 * Implementation of an {@link IdpObject} that can be used to login to
 * Shibboleth if/once the desired IdP is known.
 * 
 * @author Markus Binsteiner
 * 
 */
public class StaticIdpObject extends IdpObject {

	private final String idpName;

	/**
	 * Creates an instance using the provided IdP name.
	 * 
	 * @param idpName
	 *            the name of the IdP that is used to login.
	 */
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
