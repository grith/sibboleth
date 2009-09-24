package au.org.arcs.auth.shibboleth;

import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Iterator;

import javax.swing.JButton;
import javax.swing.JDialog;
import javax.swing.JPanel;
import javax.swing.border.EmptyBorder;

import org.python.core.PyInstance;
import org.python.core.PyObject;

public class ShibLoginDialog extends JDialog implements ShibListener {

	private final JPanel contentPanel = new JPanel();
	
	private Shibboleth shib;
	private ShibLoginPanel slcsLoginPanel = null;
	

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
			slcsLoginPanel = new ShibLoginPanel();
			contentPanel.add(slcsLoginPanel, BorderLayout.CENTER);
		}
		{
			JPanel buttonPane = new JPanel();
			buttonPane.setLayout(new FlowLayout(FlowLayout.RIGHT));
			getContentPane().add(buttonPane, BorderLayout.SOUTH);
			{
				JButton okButton = new JButton("OK");
				okButton.addActionListener(new ActionListener() {
					public void actionPerformed(ActionEvent e) {
						
						slcsLoginPanel.run();
						
					}
				});
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
		
		shib = new Shibboleth(slcsLoginPanel, slcsLoginPanel.getCredentialManager());
		shib.addShibListener(this);
		shib.openurl("https://slcs1.arcs.org.au/SLCS/login");
	}


	public void shibLoginComplete(PyInstance response) {

		Iterable<PyObject> it = response.asIterable();
		
		StringBuffer responseString = new StringBuffer();
		
		for (Iterator i = it.iterator(); i.hasNext();) {
			responseString.append(i.next());
		}
		
		System.out.println(responseString.toString());
		
		
	}

}
