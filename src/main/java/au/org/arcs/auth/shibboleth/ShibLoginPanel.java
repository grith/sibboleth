package au.org.arcs.auth.shibboleth;

import java.awt.event.KeyListener;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.util.Enumeration;
import java.util.Map;
import java.util.TreeSet;
import java.util.Vector;

import javax.swing.DefaultComboBoxModel;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JTextField;

import org.python.core.PyInstance;

import au.org.arcs.jcommons.configuration.CommonArcsProperties;

import com.jgoodies.forms.factories.FormFactory;
import com.jgoodies.forms.layout.ColumnSpec;
import com.jgoodies.forms.layout.FormLayout;
import com.jgoodies.forms.layout.RowSpec;

public class ShibLoginPanel extends JPanel implements IdpObject, ShibListener, ShibLoginEventSource {
	
	private JTextField usernameTextField;
	private JPasswordField passwordField;
	private JComboBox idpComboBox;

	private Shibboleth idpListShibClient = null;
	private Shibboleth realShibClient = null;
	
	private final String url;
	
	private boolean showLoginFailedDialog = false;

	private DefaultComboBoxModel idpModel = new DefaultComboBoxModel();

	public ShibLoginPanel(String url, boolean showLoginFailedDialog) {
		this(url);
		this.showLoginFailedDialog = showLoginFailedDialog;
	}
	/**
	 * Create the panel.
	 */
	public ShibLoginPanel(String url) {
		
		this.url = url;

		setLayout(new FormLayout(new ColumnSpec[] {
				ColumnSpec.decode("max(72dlu;default)"),
				FormFactory.RELATED_GAP_COLSPEC,
				ColumnSpec.decode("default:grow"),},
			new RowSpec[] {
				FormFactory.RELATED_GAP_ROWSPEC,
				FormFactory.DEFAULT_ROWSPEC,
				FormFactory.RELATED_GAP_ROWSPEC,
				FormFactory.DEFAULT_ROWSPEC,
				FormFactory.RELATED_GAP_ROWSPEC,
				FormFactory.DEFAULT_ROWSPEC,
				FormFactory.RELATED_GAP_ROWSPEC,}));
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
		String defaultUsername = CommonArcsProperties.getDefault().getArcsProperty(CommonArcsProperties.Property.SHIB_USERNAME);
		{
			usernameTextField = new JTextField();
			if ( defaultUsername != null && ! "".equals(defaultUsername) ) {
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
	
	public void refreshIdpList() {
		
		lockUI(true);
		
		idpModel.removeAllElements();
		idpModel.addElement("Loading idps...");
		
		idpListShibClient = new Shibboleth(this, new DummyCredentialManager());

		new Thread() {
			public void run() {

				try {
					idpListShibClient
						.openurl(url);
				} catch (Exception e) {
					e.printStackTrace();
				} finally {
					lockUI(false);
				}
				
			}
		}.start();
		
	}
	
	public WindowListener getWindowListener() {
		
		return new WindowAdapter() {
			public void windowOpened( WindowEvent e ){
				if ( usernameTextField.getText() != null && !"".equals(usernameTextField.getText()) ) {
					passwordField.requestFocus();
				}
			}
		};
		
	}
	
	public void lockUI(boolean lock) {
		
		usernameTextField.setEnabled(!lock);
		passwordField.setEnabled(!lock);
		idpComboBox.setEnabled(!lock);
		
	}
	
	public void login() {
		
		fireShibLoginStarted();

		new Thread() {
			
		public void run() {

				String idp = (String)(idpModel.getSelectedItem());
				String username = usernameTextField.getText().trim();
				char[] password = passwordField.getPassword();
				
				CommonArcsProperties.getDefault().setArcsProperty(CommonArcsProperties.Property.SHIB_USERNAME, username);
				CommonArcsProperties.getDefault().setArcsProperty(CommonArcsProperties.Property.SHIB_IDP, idp);
				
				realShibClient = new Shibboleth(new StaticIdpObject(idp), new OneTimeStaticCredentialManager(username, password));
				shibLoginStarted();
				realShibClient.addShibListener(ShibLoginPanel.this);
				realShibClient.openurl(url);
								
			}
		}.start();

	}

	public String get_idp() {
		return (String) (idpModel.getSelectedItem());
	}

	public PyInstance prompt(ShibbolethClient shibboleth) {
		return null;
	}

	public void set_idps(Map<String, String> idps) {

		idpModel.removeAllElements();
		
		for (String idp : new TreeSet<String>(idps.keySet())) {
			idpModel.addElement(idp);
		}
		
		String defaultIdp = CommonArcsProperties.getDefault().getArcsProperty(CommonArcsProperties.Property.SHIB_IDP);
		if ( defaultIdp != null && !"".equals(defaultIdp) ) {
			if ( idpModel.getIndexOf(defaultIdp) >= 0 ) {
				idpModel.setSelectedItem(defaultIdp);
			}
		}
		
		idpComboBox.setEnabled(true);
	}
	
	// Event stuff
	
	private Vector<ShibListener> shibListeners;
	
	private void fireShibLoginStarted() {
		
		if (shibListeners != null && !shibListeners.isEmpty()) {

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
				ShibListener valueChanged_l = (ShibListener) e.nextElement();
				valueChanged_l.shibLoginStarted();
			}
		}
		
	}
	
	private void fireShibLoginFailed(Exception ex) {
		
		if (shibListeners != null && !shibListeners.isEmpty()) {

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
				ShibListener valueChanged_l = (ShibListener) e.nextElement();
				valueChanged_l.shibLoginFailed(ex);
			}
		}
		
	}

	private void fireShibLoginComplete(PyInstance response) {

		if (shibListeners != null && !shibListeners.isEmpty()) {

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
				ShibListener valueChanged_l = (ShibListener) e.nextElement();
				valueChanged_l.shibLoginComplete(response);
			}
		}
	}

	// register a listener
	synchronized public void addShibListener(ShibListener l) {
		if (shibListeners == null)
			shibListeners = new Vector<ShibListener>();
		shibListeners.addElement(l);
	}

	// remove a listener
	synchronized public void removeShibListener(ShibListener l) {
		if (shibListeners == null) {
			shibListeners = new Vector<ShibListener>();
		}
		shibListeners.removeElement(l);
	}
	
	
	public void addKeyListener(KeyListener l) {
		usernameTextField.addKeyListener(l);
	}
	
	public void removeKeyListener(KeyListener l) {
		usernameTextField.removeKeyListener(l);
	}

	public void shibLoginComplete(PyInstance response) {
		
		realShibClient.removeShibListener(this);
		realShibClient = null;
		
		fireShibLoginComplete(response);		
		
		lockUI(false);
	}

	public void shibLoginFailed(Exception e) {

		fireShibLoginFailed(e);
		lockUI(false);
		
		if ( showLoginFailedDialog ) {
			JOptionPane.showMessageDialog(ShibLoginPanel.this,
			    e.getLocalizedMessage(),
			    "Login error",
			    JOptionPane.ERROR_MESSAGE);
		}

	}
	public void shibLoginStarted() {
		
		lockUI(true);

		passwordField.setText(null);
		
		fireShibLoginStarted();
	}

}
