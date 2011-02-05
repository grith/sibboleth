package grith.sibboleth;

public class CredentialManagerException extends RuntimeException {

	/**
	 * Marker exception to indicate that something went wrong at the login
	 * stage.
	 */
	public CredentialManagerException() {
		super();
	}

	public CredentialManagerException(String message) {
		super(message);
	}

	public CredentialManagerException(String message, Throwable cause) {
		super(message, cause);
	}

	public CredentialManagerException(Throwable cause) {
		super(cause);
	}

}
