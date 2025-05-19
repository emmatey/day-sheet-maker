//FLOW 
//Done
//pick file > detect valid dept > pick dept(s) to process >
//TO-Do
//generate 'big red button' dialogue. two panels. generate button. output loc button> 
//generate button is visually 'off' > saveloc clicked > open file picker > choose file > big red button comes online
//click > play sound > close program > open saveloc.
import javax.swing.*;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.util.List;

public class MainWindow implements Runnable {
   public void run() {
     JFrame frame = new JFrame("github.com/emmatey/");  
     frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
     frame.setSize(600, 480);
     frame.setLocationRelativeTo(null); //null argument sets frame to center of screen

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
     buttonPanel.setBackground(new Color(253, 187, 244));
     buttonPanel.setLayout(new BoxLayout(buttonPanel, BoxLayout.Y_AXIS));
     buttonPanel.setPreferredSize(new Dimension(600, 55));

     //Call File Picker Button
     JButton filePickerButton = FilePickerButton.createButtonWithCallback(path -> {
      String selectedFilePath = path;
      List<String> validDepartments = PythonRunner.runPreview(selectedFilePath);
      List<String> selectedDepartments = DepartmentSelectionDialog.showSelectDialog(validDepartments);
      System.out.println(selectedDepartments);
     });
     
     //Add File Picker Button
     filePickerButton.setAlignmentX(Component.CENTER_ALIGNMENT);
     filePickerButton.setFont(new Font("Monospaced", Font.BOLD, 16));
     filePickerButton.setPreferredSize(new Dimension(250, 50));
     filePickerButton.setMaximumSize(new Dimension(250, 50));
     buttonPanel.add(filePickerButton);
     
     //Create Photo Panel
     JPanel photoPanel = new JPanel();
     photoPanel.setBackground(new Color(153, 0, 0));
     photoPanel.setLayout(new FlowLayout(FlowLayout.LEFT));
     photoPanel.setPreferredSize(new Dimension(600, 335));
     photoPanel.add(new JLabel("Pictures Will Go Here!"));
     //eventually I want to point to a folder full of jpgs with a manifest file with file names. loop through manifest file and pick
     //one at random on startup. would allow to change pics without updating app.

     //Add panels to frame
     frame.getContentPane().add(header, BorderLayout.NORTH);
     frame.getContentPane().add(buttonPanel, BorderLayout.CENTER);
     frame.getContentPane().add(photoPanel, BorderLayout.SOUTH);
     frame.setVisible(true);
     frame.pack();
    }
    public static void main(String[] args) {
        SwingUtilities.invokeLater(new MainWindow());
    }
}

