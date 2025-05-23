package emmatey.gui;

import javax.swing.*;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.util.List;

public class MainWindow implements Runnable {
   private String selectedFilePath;
   private String saveDirPath;
   private List<String> selectedDepartments;
   private List<String> validDepartments;
   private JButton[] buttonReference;

   public void handleFileSelected(String filePath){
     System.out.println(filePath);
     this.validDepartments = PythonRunner.runPreview(filePath);
     System.out.println(selectedDepartments);
    }
  
    public void run() {
     JFrame mainFrame = new JFrame("github.com/emmatey/");  
     mainFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
     mainFrame.setMinimumSize(new Dimension(500, 250));
     mainFrame.setLocationRelativeTo(null); //null argument sets frame to center of screen

     // Header Panel
     JPanel header = new JPanel();
     header.setBackground(new Color(253, 187, 244)); 
     header.setPreferredSize(new Dimension(600, 55));
     
     JLabel header_text = new JLabel("💗 Daily Staffing Sheet Generator 💗", SwingConstants.CENTER);
     header_text.setFont(new Font("SansSerif", Font.BOLD, 25));
     header_text.setHorizontalAlignment(SwingConstants.CENTER); 
     header.add(header_text);
     
     // Create Button Panel
     JPanel buttonPanel = new JPanel();
     buttonPanel.setBackground(new Color(195, 177, 255));
     buttonPanel.setLayout(new BoxLayout(buttonPanel, BoxLayout.Y_AXIS));
     buttonPanel.setPreferredSize(new Dimension(600, 250)); 

     // Add File-Picker Button, Handle Output of File Picker
     JButton filePickerButton = FilePickerButton.createButtonWithCallback(path -> {
        this.selectedFilePath = path;
        // Stop Background Music on Callback
        MediaHandler.stopSound();
        
        // Create Loading Menu Object
        SimpleLoadingDialog loadingDialog = new SimpleLoadingDialog();
        loadingDialog.showAndRun(mainFrame, this, selectedFilePath, () -> {
        
        // Open Department Selection Menu on Callback
        this.selectedDepartments = DepartmentSelectionDialog.showSelectDialog(validDepartments);  
        
        // Enable Save Button on Callback
        buttonReference[0].setEnabled(true);

        // Enable Border for Visual Cue on Callback
        buttonReference[0].setBorder(BorderFactory.createLineBorder(new Color(0, 0, 0), 3, true));

        // Change Color for Visual Cue  on Callback 
        buttonReference[0].setBackground(new Color(180, 255, 200));
      });
     });
     buttonPanel.add(Box.createVerticalGlue());
     buttonPanel.add(filePickerButton);
     buttonPanel.add(Box.createRigidArea(new Dimension(0, 5))); // space between buttons
     
     // Add Save Button, Handle Output of File Picker
     JButton saveLocButton = SaveDirPicker.createButton(path -> {
        this.saveDirPath = path;
        // Stop Background Music on Callback
        MediaHandler.stopSound();
        ConfirmAndExitProgramDialogue.showDialog(
         mainFrame,
         selectedFilePath,
         saveDirPath, 
         selectedDepartments);
     });
     buttonPanel.add(saveLocButton);
     buttonPanel.add(Box.createVerticalGlue()); 
     buttonReference = new JButton[1];
     buttonReference[0] = saveLocButton;

     // Add panels to frame
     mainFrame.getContentPane().add(header, BorderLayout.NORTH);
     mainFrame.getContentPane().add(buttonPanel, BorderLayout.CENTER);
     mainFrame.setVisible(true);
     mainFrame.pack();
   }

   public static void main(String args[]){
    SwingUtilities.invokeLater(new MainWindow());
   }
}