package au.org.arcs.auth.shibboleth;

import java.util.Map;

public interface IdpObject {

	public abstract void prompt(ShibbolethClient shibboleth);

	public abstract String get_idp();

	public abstract void set_idps(Map<String, String> idps);

}