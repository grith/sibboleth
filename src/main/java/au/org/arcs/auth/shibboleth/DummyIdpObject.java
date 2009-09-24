package au.org.arcs.auth.shibboleth;

import java.util.Map;
import java.util.Set;

import org.python.core.PyInstance;

public class DummyIdpObject implements IdpObject {
	
	private Set<String> idps = null;
	
	private String sel;
	
	/* (non-Javadoc)
	 * @see au.org.arcs.auth.shibboleth.IdpObject#set_idps(java.util.Map)
	 */
	public void set_idps(Map idps) {
		this.idps = idps.keySet();
	}
	
	/* (non-Javadoc)
	 * @see au.org.arcs.auth.shibboleth.IdpObject#get_idp()
	 */
	public String get_idp() {
		return sel;
	}
	
	/* (non-Javadoc)
	 * @see au.org.arcs.auth.shibboleth.IdpObject#choose_idp()
	 */
	public void choose_idp() {
		
		if ( idps == null ) {
			throw new RuntimeException("idps not set yet");
		}
		
		if ( idps.contains("VPAC") ) {
			sel = "VPAC";
		} else {
			sel = idps.iterator().next();
		}
		
		
	}

	public PyInstance prompt(ShibbolethClient shibboleth) {
		// TODO Auto-generated method stub
		return null;
	}

}
