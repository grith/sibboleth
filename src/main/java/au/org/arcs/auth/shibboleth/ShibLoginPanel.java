package au.org.arcs.auth.shibboleth;

import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.util.Map;

import javax.swing.JComboBox;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JTextField;

import org.python.core.PyInstance;

import com.jgoodies.forms.factories.FormFactory;
import com.jgoodies.forms.layout.ColumnSpec;
import com.jgoodies.forms.layout.FormLayout;
import com.jgoodies.forms.layout.RowSpec;

public class ShibLoginPanel extends JPanel implements IdpObject {
	private JLabel lblIdp;
	private JLabel lblIdpUsername;
	private JLabel lblIdpPassword;
	private JComboBox comboBox;
	private JTextField usernameTextfield;
	private JPasswordField passwordField;
	
	private ShibbolethClient shibClient = null;
	
	private final CredentialManager cm = new CredentialManager() {
		
		public void set_title(String title) {
			// do nothing
		}
		
		public PyInstance prompt(ShibbolethClient shibboleth) {
			return shibboleth.run();
		}
		
		public String get_username() {
			return getUsernameTextfield().getText();
		}
		
		public String get_password() {
			return new String(getPasswordField().getPassword());
		}
	};

	/**
	 * Create the panel.
	 */
	public ShibLoginPanel() {
		setLayout(new FormLayout(new ColumnSpec[] {
				FormFactory.RELATED_GAP_COLSPEC,
				FormFactory.DEFAULT_COLSPEC,
				FormFactory.RELATED_GAP_COLSPEC,
				ColumnSpec.decode("default:grow"),
				FormFactory.RELATED_GAP_COLSPEC,},
			new RowSpec[] {
				FormFactory.RELATED_GAP_ROWSPEC,
				FormFactory.DEFAULT_ROWSPEC,
				FormFactory.RELATED_GAP_ROWSPEC,
				FormFactory.DEFAULT_ROWSPEC,
				FormFactory.RELATED_GAP_ROWSPEC,
				FormFactory.DEFAULT_ROWSPEC,
				FormFactory.RELATED_GAP_ROWSPEC,}));
		add(getLblIdp(), "2, 2, right, default");
		add(getComboBox(), "4, 2, fill, default");
		add(getLblIdpUsername(), "2, 4, right, default");
		add(getUsernameTextfield(), "4, 4, fill, default");
		add(getLblIdpPassword(), "2, 6, right, default");
		add(getPasswordField(), "4, 6, fill, default");

	}

	public String get_password() {
		return new String(getPasswordField().getPassword());
	}

	public String get_username() {
		return getUsernameTextfield().getText();
	}

	public PyInstance prompt(ShibbolethClient shibboleth) {

		this.shibClient = shibboleth;
		
		return null;
		
	}
	
	public CredentialManager getCredentialManager() {
		
		return cm;
		
	}

	public void set_title(String title) {

		System.out.println(title);
	}

	public String get_idp() {
		return (String)getComboBox().getSelectedItem();
	}

	public void set_idps(Map<String, String> idps) {

		getComboBox().removeAllItems();
		for ( String key : idps.keySet() ) {
			getComboBox().addItem(key);
		}
	}
	
	public void run() {
		
		shibClient.run();
		
	}

	private JLabel getLblIdp() {
		if (lblIdp == null) {
			lblIdp = new JLabel("Idp");
		}
		return lblIdp;
	}
	private JLabel getLblIdpUsername() {
		if (lblIdpUsername == null) {
			lblIdpUsername = new JLabel("Idp username");
		}
		return lblIdpUsername;
	}
	private JLabel getLblIdpPassword() {
		if (lblIdpPassword == null) {
			lblIdpPassword = new JLabel("Idp password");
		}
		return lblIdpPassword;
	}
	private JComboBox getComboBox() {
		if (comboBox == null) {
			comboBox = new JComboBox();
		}
		return comboBox;
	}
	private JTextField getUsernameTextfield() {
		if (usernameTextfield == null) {
			usernameTextfield = new JTextField();
			usernameTextfield.setColumns(10);
		}
		return usernameTextfield;
	}
	private JPasswordField getPasswordField() {
		if (passwordField == null) {
			passwordField = new JPasswordField();
		}
		return passwordField;
	}
	
	public void addKeyListener(KeyListener l) {
		getUsernameTextfield().addKeyListener(l);
	}
	
	public void removeKeyListener(KeyListener l) {
		getUsernameTextfield().removeKeyListener(l);
	}
}
