package au.org.arcs.auth.shibboleth;

import java.util.Map;

public interface IdpObject {

	public abstract void set_idps(Map idps);

	public abstract String get_idp();

	public abstract void choose_idp();

}