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
     buttonPanel.setBackground(new Color(119, 221, 119));
     buttonPanel.setLayout(new BoxLayout(buttonPanel, BoxLayout.Y_AXIS));
     buttonPanel.setPreferredSize(new Dimension(600, 55));

     //Create Photo Panel
     JPanel checkBoxPanel = new JPanel();
     checkBoxPanel.setBackground(new Color(153, 0, 0));
     checkBoxPanel.setLayout(new FlowLayout(FlowLayout.LEFT));
     checkBoxPanel.setPreferredSize(new Dimension(600, 335));
     checkBoxPanel.add(new JLabel("Pictures Will Go Here!"));

     //Add File Picker Button
     JButton filePickerButton = FilePickerButton.createButtonWithCallback(path -> {
      String selectedFilePath = path;
      List<String> validDepartments = PythonRunner.runPreview(selectedFilePath);
      List<String> selectedDepartments = DepartmentSelectionDialog.showSelectDialog(validDepartments);
      System.out.println(selectedDepartments);
     });
     
     filePickerButton.setAlignmentX(Component.CENTER_ALIGNMENT);
     filePickerButton.setFont(new Font("Monospaced", Font.BOLD, 16));
     filePickerButton.setPreferredSize(new Dimension(250, 50));
     filePickerButton.setMaximumSize(new Dimension(250, 50));
     buttonPanel.add(filePickerButton);

     //Add panels to frame
     frame.getContentPane().add(header, BorderLayout.NORTH);
     frame.getContentPane().add(buttonPanel, BorderLayout.CENTER);
     frame.getContentPane().add(checkBoxPanel, BorderLayout.SOUTH);
     frame.setVisible(true);
     frame.pack();
    }
    public static void main(String[] args) {
        SwingUtilities.invokeLater(new MainWindow());
    }
}

