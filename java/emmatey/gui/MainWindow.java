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

   private void handleFileSelected(String filePath){
     System.out.println(filePath);
     List<String> validDepartments = PythonRunner.runPreview(filePath);
     this.selectedDepartments = DepartmentSelectionDialog.showSelectDialog(validDepartments);
     System.out.println(selectedDepartments);
    }
   
   public void run() {
     JFrame mainFrame = new JFrame("github.com/emmatey/");  
     mainFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
     mainFrame.setSize(600, 480);
     mainFrame.setLocationRelativeTo(null); //null argument sets frame to center of screen

     //Header Panel
     JPanel header = new JPanel();
     header.setBackground(new Color(253, 187, 244)); 
     header.setPreferredSize(new Dimension(600, 75));
     
     JLabel header_text = new JLabel("💗 Daily Staffing Sheet Generator 💗", SwingConstants.CENTER);
     header_text.setFont(new Font("SansSerif", Font.BOLD, 24));
     header_text.setHorizontalAlignment(SwingConstants.CENTER);
     header.add(header_text);
     
     //Create Button Panel
     JPanel buttonPanel = new JPanel();
     buttonPanel.setBackground(new Color(195, 177, 255));
     buttonPanel.setLayout(new BoxLayout(buttonPanel, BoxLayout.Y_AXIS));
     buttonPanel.setPreferredSize(new Dimension(600, 400));
     
     //Add File-Picker Button
     JButton filePickerButton = FilePickerButton.createButtonWithCallback(path -> {
        this.selectedFilePath = path;
        handleFileSelected(selectedFilePath);
     });
     buttonPanel.add(filePickerButton);
     
     //Add Save Button
     JButton saveLocButton = SaveDirPicker.createButton(path -> {
        this.saveDirPath = path;
        ConfirmAndExitProgramDialogue.showDialog(
         mainFrame,
         selectedFilePath,
         saveDirPath, 
         selectedDepartments);
     });
     buttonPanel.add(saveLocButton);

     //Add panels to frame
     mainFrame.getContentPane().add(header, BorderLayout.NORTH);
     mainFrame.getContentPane().add(buttonPanel, BorderLayout.CENTER);
     mainFrame.setVisible(true);
     mainFrame.pack();
   }

   public static void main(String args[]){
    SwingUtilities.invokeLater(new MainWindow());
   }
}