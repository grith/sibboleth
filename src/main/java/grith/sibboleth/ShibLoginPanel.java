package grith.sibboleth;

import grisu.jcommons.configuration.CommonGridProperties;
import grisu.jcommons.interfaces.IdpListener;
import grisu.jcommons.utils.NewHttpProxyEvent;

import java.awt.event.KeyListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.util.Enumeration;
import java.util.SortedSet;
import java.util.Vector;

import javax.swing.DefaultComboBoxModel;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JTextField;

import org.apache.commons.lang.StringUtils;
import org.bushe.swing.event.EventBus;
import org.bushe.swing.event.EventSubscriber;
import org.python.core.PyInstance;

import com.jgoodies.forms.factories.FormFactory;
import com.jgoodies.forms.layout.ColumnSpec;
import com.jgoodies.forms.layout.FormLayout;
import com.jgoodies.forms.layout.RowSpec;

/**
 * Reusable Swing component that can be used to display a shib-login component
 * in your Swing app.
 * 
 * You'd create it using one of the constructors and then add a custom
 * {@link ShibListener} to the object.
 * 
 * @author Markus Binsteiner
 * 
 */
public class ShibLoginPanel extends JPanel implements ShibListener,
ShibLoginEventSource, IdpListener, EventSubscriber<NewHttpProxyEvent> {

	private static final long serialVersionUID = 3143352249184524656L;

	public static final String LOADING_IDPS_STRING = "Loading idps...";
	public static final String COULD_NOT_LOAD_IDP_LIST_STRING = "Failed to get list of idps.";

	private JTextField usernameTextField;
	private JPasswordField passwordField;
	private JComboBox idpComboBox;

	private Shibboleth idpListShibClient = null;
	private Shibboleth realShibClient = null;

	private final String url;

	private boolean showLoginFailedDialog = false;

	private final DefaultComboBoxModel idpModel = new DefaultComboBoxModel();

	private Thread refreshIdpThread;

	// implement idplistener exchange if you want to remove final here...
	final private IdpObject idpObject = new IdpObject() {

		@Override
		public String get_idp() {
			return ShibLoginPanel.this.get_idp();
		}

		@Override
		public PyInstance prompt(ShibbolethClient shibboleth) {
			return null;
		}
	};

	private Vector<ShibListener> shibListeners;

	/**
	 * Create the panel using the specified start url.
	 * 
	 * @param url
	 *            the url of the WAYF/DS.
	 */
	public ShibLoginPanel(String url) {

		EventBus.subscribe(NewHttpProxyEvent.class, this);
		idpObject.addIdpListener(this);
		this.url = url;

		setLayout(new FormLayout(new ColumnSpec[] {
				ColumnSpec.decode("max(72dlu;default)"),
				FormFactory.RELATED_GAP_COLSPEC,
				ColumnSpec.decode("default:grow"), }, new RowSpec[] {
				FormFactory.RELATED_GAP_ROWSPEC, FormFactory.DEFAULT_ROWSPEC,
				FormFactory.RELATED_GAP_ROWSPEC, FormFactory.DEFAULT_ROWSPEC,
				FormFactory.RELATED_GAP_ROWSPEC, FormFactory.DEFAULT_ROWSPEC,
				FormFactory.RELATED_GAP_ROWSPEC, }));
		{
			JLabel lblIdp = new JLabel("Idp:");
			add(lblIdp, "1, 2, right, default");
		}
		{
			idpComboBox = new JComboBox(idpModel);
			idpModel.addElement("Loading idp list...");
			idpComboBox.setEnabled(false);

			add(idpComboBox, "3, 2, fill, default");

		}
		{
			JLabel lblUsername = new JLabel("Username:");
			add(lblUsername, "1, 4, right, default");
		}
		String defaultUsername = CommonGridProperties.getDefault()
		.getGridProperty(CommonGridProperties.Property.SHIB_USERNAME);
		{
			usernameTextField = new JTextField();
			if ((defaultUsername != null) && !"".equals(defaultUsername)) {
				usernameTextField.setText(defaultUsername);
			}
			add(usernameTextField, "3, 4, fill, default");
			usernameTextField.setColumns(10);
		}
		{
			JLabel lblPassword = new JLabel("Password:");
			add(lblPassword, "1, 6, right, default");
		}
		{
			passwordField = new JPasswordField();
			add(passwordField, "3, 6, fill, default");
		}

		refreshIdpList();

	}

	/**
	 * Create the panel using the specified start url.
	 * 
	 * @param url
	 *            the url of the WAYF/DS.
	 * @param showLoginFailedDialog
	 *            whether to display a JDialog when login fails or not. You can
	 *            display your own error message through the attached listener
	 *            if you specify false here.
	 */
	public ShibLoginPanel(String url, boolean showLoginFailedDialog) {
		this(url);
		this.showLoginFailedDialog = showLoginFailedDialog;
	}

	/**
	 * Adds an {@link IdpListener}.
	 * 
	 * @param l
	 *            the listener
	 */
	synchronized public void addIdpListener(IdpListener l) {
		idpObject.addIdpListener(l);
	}

	@Override
	public void addKeyListener(KeyListener l) {
		usernameTextField.addKeyListener(l);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * grith.sibboleth.ShibLoginEventSource#addShibListener(grith.sibboleth.
	 * ShibListener)
	 */
	synchronized public void addShibListener(ShibListener l) {
		if (shibListeners == null) {
			shibListeners = new Vector<ShibListener>();
		}
		shibListeners.addElement(l);
	}

	private void fireShibLoginComplete(PyInstance response) {

		if ((shibListeners != null) && !shibListeners.isEmpty()) {

			// make a copy of the listener list in case
			// anyone adds/removes mountPointsListeners
			Vector<ShibListener> shibChangeTargets;
			synchronized (this) {
				shibChangeTargets = (Vector<ShibListener>) shibListeners
				.clone();
			}

			// walk through the listener list and
			// call the gridproxychanged method in each
			Enumeration<ShibListener> e = shibChangeTargets.elements();
			while (e.hasMoreElements()) {
				ShibListener valueChanged_l = e.nextElement();
				valueChanged_l.shibLoginComplete(response);
			}
		}
	}

	private void fireShibLoginFailed(Exception ex) {

		if ((shibListeners != null) && !shibListeners.isEmpty()) {

			// make a copy of the listener list in case
			// anyone adds/removes mountPointsListeners
			Vector<ShibListener> shibChangeTargets;
			synchronized (this) {
				shibChangeTargets = (Vector<ShibListener>) shibListeners
				.clone();
			}

			// walk through the listener list and
			// call the gridproxychanged method in each
			Enumeration<ShibListener> e = shibChangeTargets.elements();
			while (e.hasMoreElements()) {
				ShibListener valueChanged_l = e.nextElement();
				valueChanged_l.shibLoginFailed(ex);
			}
		}

	}

	// Event stuff

	private void fireShibLoginStarted() {

		if ((shibListeners != null) && !shibListeners.isEmpty()) {

			// make a copy of the listener list in case
			// anyone adds/removes mountPointsListeners
			Vector<ShibListener> shibChangeTargets;
			synchronized (this) {
				shibChangeTargets = (Vector<ShibListener>) shibListeners
				.clone();
			}

			// walk through the listener list and
			// call the gridproxychanged method in each
			Enumeration<ShibListener> e = shibChangeTargets.elements();
			while (e.hasMoreElements()) {
				ShibListener valueChanged_l = e.nextElement();
				valueChanged_l.shibLoginStarted();
			}
		}

	}

	/**
	 * Returns the currently user-selected IdP.
	 * 
	 * @return the IdP name
	 */
	public String get_idp() {
		return (String) (idpModel.getSelectedItem());
	}

	public WindowListener getWindowListener() {

		return new WindowAdapter() {
			@Override
			public void windowOpened(WindowEvent e) {
				if ((usernameTextField.getText() != null)
						&& !"".equals(usernameTextField.getText())) {
					passwordField.requestFocus();
				}
			}
		};

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * grisu.jcommons.interfaces.IdpListener#idpListLoaded(java.util.SortedSet)
	 */
	public void idpListLoaded(SortedSet<String> idpList) {

		idpModel.removeAllElements();

		for (String idp : idpList) {
			idpModel.addElement(idp);
		}

		String defaultIdp = CommonGridProperties.getDefault().getGridProperty(
				CommonGridProperties.Property.SHIB_IDP);
		if ((defaultIdp != null) && !"".equals(defaultIdp)) {
			if (idpModel.getIndexOf(defaultIdp) >= 0) {
				idpModel.setSelectedItem(defaultIdp);
			}
		}

		idpComboBox.setEnabled(true);
	}

	/**
	 * Used to lock/disable the UI elements of this panel.
	 * 
	 * @param lock
	 *            true for disabling, false for enabling this panel
	 */
	public void lockUI(boolean lock) {

		usernameTextField.setEnabled(!lock);
		passwordField.setEnabled(!lock);
		idpComboBox.setEnabled(!lock);

	}

	/**
	 * Call this method to start the login process. Usually attached to the
	 * action associated with a login button.
	 */
	public void login() {

		fireShibLoginStarted();

		new Thread() {

			@Override
			public void run() {

				String idp = (String) (idpModel.getSelectedItem());
				if (StringUtils.isBlank(idp) || LOADING_IDPS_STRING.equals(idp)) {
					return;
				}
				String username = usernameTextField.getText().trim();
				char[] password = passwordField.getPassword();

				CommonGridProperties.getDefault().setGridProperty(
						CommonGridProperties.Property.SHIB_USERNAME, username);
				if (!idp.equals(COULD_NOT_LOAD_IDP_LIST_STRING)
						&& !idp.equals(LOADING_IDPS_STRING)) {
					CommonGridProperties.getDefault().setGridProperty(
							CommonGridProperties.Property.SHIB_IDP, idp);
				}

				try {
					realShibClient.removeShibListener(ShibLoginPanel.this);
				} catch (Exception e) {
					//
				}

				try {
					realShibClient = new Shibboleth(new StaticIdpObject(idp),
							new OneTimeStaticCredentialManager(username,
									password));
					realShibClient.addShibListener(ShibLoginPanel.this);
					shibLoginStarted();
					realShibClient.openurl(url);
				} catch (Exception e) {
					e.printStackTrace();
					shibLoginFailed(e);
					// fireShibLoginFailed(e);
				}

			}
		}.start();

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.bushe.swing.event.EventSubscriber#onEvent(java.lang.Object)
	 */
	public void onEvent(NewHttpProxyEvent arg0) {

		// try to reload idplist
		refreshIdpList();

	}

	/**
	 * Used from within the python code.
	 * 
	 * Don't call this manually.
	 * 
	 * @param shibboleth
	 *            the controller object
	 * @return the response
	 */
	public PyInstance prompt(ShibbolethClient shibboleth) {
		return null;
	}

	/**
	 * Call this to refresh the list of the displayed IdPs.
	 * 
	 * Usually called after http proxy settings change or such. You probably
	 * don't need to do that though since it'll be done automatically.
	 */
	public void refreshIdpList() {

		lockUI(true);

		idpModel.removeAllElements();

		final String lastIdp = CommonGridProperties.getDefault()
		.getGridProperty(CommonGridProperties.Property.SHIB_IDP);

		if (StringUtils.isNotBlank(lastIdp)) {
			idpModel.addElement(lastIdp);
			lockUI(false);
		} else {
			idpModel.addElement(LOADING_IDPS_STRING);
		}

		idpListShibClient = new Shibboleth(idpObject,
				new DummyCredentialManager());

		try {
			refreshIdpThread.interrupt();
		} catch (Exception e) {
			// doesn't matter
		}

		refreshIdpThread = new Thread() {
			@Override
			public void run() {

				try {
					idpListShibClient.openurl(url);
				} catch (Exception e) {
					if (StringUtils.isBlank(lastIdp)) {
						idpModel.removeAllElements();
						idpModel.addElement(COULD_NOT_LOAD_IDP_LIST_STRING);
					}
					e.printStackTrace(System.err);
				} finally {
					lockUI(false);
				}

			}
		};

		refreshIdpThread.start();

	}

	/**
	 * Removes an {@link IdpListener}.
	 * 
	 * @param l
	 *            the listener
	 */
	synchronized public void removeIdpListener(IdpListener l) {
		idpObject.removeIdpListener(l);
	}

	@Override
	public void removeKeyListener(KeyListener l) {
		usernameTextField.removeKeyListener(l);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * grith.sibboleth.ShibLoginEventSource#removeShibListener(grith.sibboleth
	 * .ShibListener)
	 */
	synchronized public void removeShibListener(ShibListener l) {
		if (shibListeners == null) {
			shibListeners = new Vector<ShibListener>();
		}
		shibListeners.removeElement(l);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * grith.sibboleth.ShibListener#shibLoginComplete(org.python.core.PyInstance
	 * )
	 */
	public void shibLoginComplete(PyInstance response) {

		realShibClient.removeShibListener(this);
		realShibClient = null;

		fireShibLoginComplete(response);

		lockUI(false);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see grith.sibboleth.ShibListener#shibLoginFailed(java.lang.Exception)
	 */
	public void shibLoginFailed(Exception e) {

		fireShibLoginFailed(e);
		lockUI(false);

		if (showLoginFailedDialog) {
			JOptionPane.showMessageDialog(ShibLoginPanel.this,
					e.getLocalizedMessage(), "Login error",
					JOptionPane.ERROR_MESSAGE);
		}

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see grith.sibboleth.ShibListener#shibLoginStarted()
	 */
	public void shibLoginStarted() {

		lockUI(true);

		passwordField.setText(null);

		fireShibLoginStarted();
	}
}
