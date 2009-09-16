package au.org.arcs.auth.shibboleth;

import java.util.Map;
import java.util.Set;

public class IdpObject {
	
	private Set<String> idps = null;
	
	private String sel;
	
	public void set_idps(Map idps) {
		this.idps = idps.keySet();
	}
	
	public String get_idp() {
		return sel;
	}
	
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

}
