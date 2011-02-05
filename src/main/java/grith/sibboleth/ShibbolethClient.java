package grith.sibboleth;

import org.python.core.PyInstance;
import org.python.core.PyObject;

/**
 * Interface that is needed for the whole (j/p)ython - Java wrapping.
 * 
 * You don't need to concern your pretty little head with this...
 * 
 * @author Markus Binsteiner
 * 
 */
public interface ShibbolethClient {

	public void add_listener(PyObject listener);

	public PyInstance get_response();

	public PyInstance openurl(String url);

	public PyInstance run();

}
