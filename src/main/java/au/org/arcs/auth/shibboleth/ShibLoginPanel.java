package au.org.arcs.auth.shibboleth;

import java.awt.event.KeyListener;
import java.util.Enumeration;
import java.util.Iterator;
import java.util.Map;
import java.util.TreeSet;
import java.util.Vector;

import javax.swing.DefaultComboBoxModel;
import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;

import org.python.core.PyInstance;
import org.python.core.PyObject;

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

	private DefaultComboBoxModel idpModel = new DefaultComboBoxModel();

	/**
	 * Create the panel.
	 */
	public ShibLoginPanel() {

		idpListShibClient = new Shibboleth(this, new DummyCredentialManager());

		new Thread() {
			public void run() {

				idpListShibClient
						.openurl("https://slcs1.arcs.org.au/SLCS/login");
			}
		}.start();

		setLayout(new FormLayout(new ColumnSpec[] {
				FormFactory.RELATED_GAP_COLSPEC, FormFactory.DEFAULT_COLSPEC,
				FormFactory.RELATED_GAP_COLSPEC,
				ColumnSpec.decode("default:grow"),
				FormFactory.RELATED_GAP_COLSPEC, }, new RowSpec[] {
				FormFactory.RELATED_GAP_ROWSPEC, FormFactory.DEFAULT_ROWSPEC,
				FormFactory.RELATED_GAP_ROWSPEC, FormFactory.DEFAULT_ROWSPEC,
				FormFactory.RELATED_GAP_ROWSPEC, FormFactory.DEFAULT_ROWSPEC,
				FormFactory.RELATED_GAP_ROWSPEC, }));
		{
			JLabel lblIdp = new JLabel("Idp:");
			add(lblIdp, "2, 2, right, default");
		}
		{
			idpComboBox = new JComboBox(idpModel);
			idpModel.addElement("Loading idp list...");
			idpComboBox.setEnabled(false);
			
			add(idpComboBox, "4, 2, fill, default");
			
		}
		{
			JLabel lblUsername = new JLabel("Username:");
			add(lblUsername, "2, 4");
		}
		{
			usernameTextField = new JTextField();
			add(usernameTextField, "4, 4, fill, default");
			usernameTextField.setColumns(10);
		}
		{
			JLabel lblPassword = new JLabel("Password:");
			add(lblPassword, "2, 6, right, default");
		}
		{
			passwordField = new JPasswordField();
			add(passwordField, "4, 6, fill, default");
		}

	}
	
	public void lockUI(boolean lock) {
		
		usernameTextField.setEnabled(!lock);
		passwordField.setEnabled(!lock);
		idpComboBox.setEnabled(!lock);
		
	}
	
	public void login() {
		
		lockUI(true);
		
		new Thread() {
		public void run() {

				String idp = (String)(idpModel.getSelectedItem());
				String username = usernameTextField.getText().trim();
				char[] password = passwordField.getPassword();
				
				realShibClient = new Shibboleth(new StaticIdpObject(idp), new StaticCredentialManager(username, password));
				realShibClient.addShibListener(ShibLoginPanel.this);
				realShibClient.openurl("https://slcs1.arcs.org.au/SLCS/login");
								
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
		
		idpComboBox.setEnabled(true);
	}
	
	// Event stuff
	
	private Vector<ShibListener> shibListeners;

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

}
