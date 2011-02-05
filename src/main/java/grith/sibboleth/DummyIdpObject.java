package grith.sibboleth;

import grisu.jcommons.utils.DefaultGridSecurityProvider;

import org.python.core.PyInstance;

/**
 * Dummy implementation of an {@link IdpObject}.
 * 
 * Used to get a list of all availabe IdPs in order to display to the user
 * interactively.
 * 
 * @author Markus Binsteiner
 * 
 */
public class DummyIdpObject extends IdpObject {

	public static void main(String[] args) throws InterruptedException {

		java.security.Security.addProvider(new DefaultGridSecurityProvider());

		java.security.Security.setProperty("ssl.TrustManagerFactory.algorithm",
		"TrustAllCertificates");


		IdpObject idpO = new DummyIdpObject();

		CredentialManager cm = new DummyCredentialManager();

		Shibboleth shib = new Shibboleth(idpO, cm);

		String url = "https://slcs1.arcs.org.au/SLCS/login";
		shib.openurl(url);

		for (String idp : idpO.getIdps()) {
			System.out.println(idp);
		}

		System.out.println("Finished.");

	}

	private final String sel = "Dummy";

	@Override
	public String get_idp() {
		return sel;
	}

	@Override
	public PyInstance prompt(ShibbolethClient shibboleth) {
		return null;
	}

}
