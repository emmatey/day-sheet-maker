package emmatey.gui;

import java.awt.*;
import javax.swing.*;

import java.io.File;
import java.util.List;

public class ConfirmAndExitProgramDialogue extends JDialog {

    public static void handleSave(String selectedFilePath, String savePath, List<String>selectedDepartments){
        System.out.println(savePath);
        PythonRunner.runGenerate(
        selectedFilePath, 
        savePath, 
        selectedDepartments);
     };
    
    public static void showDialog(JFrame parentFrame, String selectedFilePath, String savePath, List<String>selectedDepartments){
        // Create Parrent Window
        JDialog dialogue = new JDialog(parentFrame, "Waiting Room", true);

        // Create Holder Panel
        JPanel holder = new JPanel();
        holder.setLayout(new BoxLayout(holder, BoxLayout.Y_AXIS));

        // Create Header Panel
        JPanel header = new JPanel();
        header.setBackground(new Color(128, 172, 221)); 

        // Add Header Text
        JLabel header_text = new JLabel("A Moment of Tranquility", SwingConstants.CENTER);
        header_text.setFont(new Font("SansSerif", Font.BOLD, 24));
        header_text.setHorizontalAlignment(SwingConstants.CENTER);
        header.add(header_text);
        holder.add(header);

        // Create and Populate Media Panel
        JPanel photoPanel = new JPanel();
        photoPanel.setBackground(new Color(128, 172, 221));
        JLabel media = MediaHandler.getGifLabel("hangingTree.gif");
        media.setAlignmentX(CENTER_ALIGNMENT);
        photoPanel.add(media);
        holder.add(photoPanel);
        
        // Create Loading Bar and Button Panel
        JPanel progressAndClosePanel = new JPanel();
        holder.add(progressAndClosePanel);

        // Create Progress Bar
        JProgressBar progressBar = new JProgressBar();
        progressBar.setIndeterminate(true);
        progressBar.setString("Generating Day Sheets....Beep Boop");
        progressBar.setStringPainted(true);
        progressAndClosePanel.add(progressBar);

        // Create JButton, Confirm and Close
        JButton closeButton = new JButton("Save and Exit");
        closeButton.setEnabled(false);
        closeButton.addActionListener(event -> {
            try {
                Desktop.getDesktop().open(new File(savePath));
            } catch (Exception ex) {
                ex.printStackTrace();
                JOptionPane.showMessageDialog(parentFrame, "Could not open folder:\n" + savePath);
                return;
            }

            System.exit(0);
        });
        progressAndClosePanel.add(closeButton);

        // Create Background Thread
        SwingWorker<Void, Void> lilLoader = new SwingWorker<Void, Void>() {
            @Override
            protected Void doInBackground(){
                handleSave(selectedFilePath, savePath, selectedDepartments);
                return null;
            }
            
            @Override
            protected void done(){
                // Loading Bar
                progressBar.setIndeterminate(false);
                progressBar.setString("Complete!");

                // Close Button
                closeButton.setEnabled(true);
                closeButton.setBackground(new Color(180, 255, 200));

                // Audio Cue
                Toolkit.getDefaultToolkit().beep();
            }
        };

        // Start Background Tasks
        MediaHandler.playSound("forestAudio.wav", true);
        lilLoader.execute();

        // Add panels to frame
        dialogue.add(holder);
        dialogue.pack();
        dialogue.setLocationRelativeTo(parentFrame);
        dialogue.setVisible(true);
    }

}