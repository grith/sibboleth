package au.org.arcs.auth.shibboleth;

import java.util.SortedSet;

public interface IdpListener {
	
	public void idpListLoaded(SortedSet<String> idpList);

}
