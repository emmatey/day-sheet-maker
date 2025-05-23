package emmatey.gui;

import java.awt.BorderLayout;

import javax.swing.BorderFactory;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JProgressBar;
import javax.swing.SwingWorker;

public class SimpleLoadingDialog {

    private JDialog dialog;

    public void showAndRun(JFrame parent, MainWindow mainWindow, String selectedFilePath, Runnable onDone) {
        dialog = new JDialog(parent, "Processing...", true);
        dialog.setDefaultCloseOperation(JDialog.DO_NOTHING_ON_CLOSE);

        JPanel panel = new JPanel(new BorderLayout(10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));

        JLabel label = new JLabel("Processing file, please wait...");
        JProgressBar progressBar = new JProgressBar();
        progressBar.setIndeterminate(true);

        panel.add(label, BorderLayout.NORTH);
        panel.add(progressBar, BorderLayout.CENTER);

        dialog.getContentPane().add(panel);
        dialog.pack();
        dialog.setLocationRelativeTo(parent);

        SwingWorker<Void, Void> worker = new SwingWorker<>() {
            @Override
            protected Void doInBackground() {
                MediaHandler.playSound("jazzCafeCrowd.wav", true);
                mainWindow.handleFileSelected(selectedFilePath);
                return null;
            }

            @Override
            protected void done() {
                MediaHandler.stopSound();
                dialog.setVisible(false);
                dialog.dispose();
                onDone.run();
            }
        };

        worker.execute();
        dialog.setVisible(true);
    }
}
