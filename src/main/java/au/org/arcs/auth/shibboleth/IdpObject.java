package au.org.arcs.auth.shibboleth;

import java.util.Map;

import org.python.core.PyInstance;

public interface IdpObject {

	public abstract PyInstance prompt(ShibbolethClient shibboleth);

	public abstract String get_idp();

	public abstract void set_idps(Map<String, String> idps);

}