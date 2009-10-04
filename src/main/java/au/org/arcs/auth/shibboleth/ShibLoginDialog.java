package au.org.arcs.auth.shibboleth;

import java.awt.BorderLayout;
import java.awt.FlowLayout;

import javax.swing.JButton;
import javax.swing.JDialog;
import javax.swing.JPanel;
import javax.swing.border.EmptyBorder;
import javax.swing.AbstractAction;
import java.awt.event.ActionEvent;
import javax.swing.Action;

public class ShibLoginDialog extends JDialog {

	private final JPanel contentPanel = new JPanel();
	private final Action action = new LoginAction();
	private ShibLoginPanel shibLoginPanel;

	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		try {
			ShibLoginDialog dialog = new ShibLoginDialog();
			dialog.setDefaultCloseOperation(JDialog.DISPOSE_ON_CLOSE);
			dialog.setVisible(true);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	/**
	 * Create the dialog.
	 */
	public ShibLoginDialog() {
		
		java.security.Security.addProvider(new ArcsSecurityProvider());

		java.security.Security.setProperty("ssl.TrustManagerFactory.algorithm",
				"TrustAllCertificates");
		
		setBounds(100, 100, 450, 300);
		getContentPane().setLayout(new BorderLayout());
		contentPanel.setBorder(new EmptyBorder(5, 5, 5, 5));
		getContentPane().add(contentPanel, BorderLayout.CENTER);
		contentPanel.setLayout(new BorderLayout(0, 0));
		{
			shibLoginPanel = new ShibLoginPanel();
			contentPanel.add(shibLoginPanel, BorderLayout.CENTER);
		}
		{
			JPanel buttonPane = new JPanel();
			buttonPane.setLayout(new FlowLayout(FlowLayout.RIGHT));
			getContentPane().add(buttonPane, BorderLayout.SOUTH);
			{
				JButton okButton = new JButton("OK");
				okButton.setAction(action);
				okButton.setActionCommand("OK");
				buttonPane.add(okButton);
				getRootPane().setDefaultButton(okButton);
			}
			{
				JButton cancelButton = new JButton("Cancel");
				cancelButton.setActionCommand("Cancel");
				buttonPane.add(cancelButton);
			}
		}
	}

	private class LoginAction extends AbstractAction {
		public LoginAction() {
			putValue(NAME, "Login");
			putValue(SHORT_DESCRIPTION, "Logging in");
		}
		public void actionPerformed(ActionEvent e) {
			
			shibLoginPanel.login();
			
		}
	}
}
